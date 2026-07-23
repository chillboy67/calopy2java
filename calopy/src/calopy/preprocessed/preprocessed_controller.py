import datetime
import io

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
from scipy.stats import sem
from shiny import reactive, render, ui, Session
from shinywidgets import render_widget

from calopy.calopy_store import caliData, calopyStore
from calopy.calopy_ui import PREPROCESSING
from calopy.maths.series_utils import getAreasWhereDatetimIndexIs, getIndexOf24HourInterval
from calopy.preprocessed.DialogEditAdditionalData import additional_data_update, \
                                                         dialogEditAdditionalData_shiny
from calopy.preprocessed.DialogEditMetabolicVariable import metabolic_variable_update, \
                                                            dialogEditMetabolicVariable_shiny, \
                                                            dialogEditMetabolicVariable
from calopy.preprocessed.preprocessed_shiny import preprocessed_shiny
from calopy.shared_ui.ICdataPlot import calorimetryDataPlot
from calopy.shared_ui.plot_config import COLOR_DATECHANGE, COLOR_NIGHTTIME, create_empty_plot, \
                                         get_color_samples

# pio.kaleido.scope.mathjax = None  ### avoids mathjax message for first pdf export https://github.com/plotly/plotly.py/issues/3469

preprocessed_load_state_toggle = reactive.Value(True)


def preprocessed_load_state():
    print("preprocessed_load_state")
    preprocessed_load_state_toggle.set(not preprocessed_load_state_toggle())


def preprocessed(input, output, session):
    preprocessed_update_toggle = reactive.Value(True)
    preprocessed_measurement = None
    preprocessed_grouped = None

    def preprocessed_update():
        print("preprocessed_update_ui")
        preprocessed_update_toggle.set(not preprocessed_update_toggle())

    @output
    @render.ui
    def preprocessed_ui():
        print("preprocessed_ui")
        return preprocessed_shiny

    @reactive.Effect
    @reactive.event(input.selected_feature)
    def preprocessedSelectedFeature():
        print("selected_feature")
        if input.selected_feature() == PREPROCESSING:
            preprocessed_load_state()
            preprocessed_update()

    @reactive.Effect
    @reactive.event(preprocessed_load_state_toggle)
    def reloadState():
        print("preprocessed reloadState")
        preprocessed_load_state()
        preprocessed_update()

    def preprocessed_load_state():
        print("load_state")
        try:
            ui.update_select(
                "preprocessed_current_measurement",
                choices=caliData(session).measurements(),
                selected=preprocessed_measurement,
            )
            ui.update_select(
                "preprocessed_grouped",
                choices=caliData(session).getCategoricalColumns(),
                selected=caliData(session).groupedBy,
            )
            ui.update_date(
                "preprocessed_measurement_start_date",
                value=caliData(session).croppedStart.date(),
            )
            ui.update_date(
                "preprocessed_measurement_end_date",
                value=caliData(session).croppedEnd.date(),
            )
            ui.update_numeric(
                "preprocessed_measurement_start_time_hour",
                value=caliData(session).croppedStart.time().hour,
            )
            ui.update_numeric(
                "preprocessed_measurement_start_time_minute",
                value=caliData(session).croppedStart.time().minute,
            )
            ui.update_numeric(
                "preprocessed_measurement_end_time_hour",
                value=caliData(session).croppedEnd.time().hour,
            )
            ui.update_numeric(
                "preprocessed_measurement_end_time_minute",
                value=caliData(session).croppedEnd.time().minute,
            )
            ui.update_numeric("preprocessed_day_start_hour", value=caliData(session).day.hour)
            ui.update_numeric("preprocessed_day_start_minute", value=caliData(session).day.minute)
            ui.update_numeric("preprocessed_night_start_hour", value=caliData(session).night.hour)
            ui.update_numeric(
                "preprocessed_night_start_minute", value=caliData(session).night.minute
            )
            ui.update_checkbox(
                "preprocessed_all_same_day_start",
                value=caliData(session).allSameDayStart,
            )
            ui.update_selectize(
                "preprocessed_excluded_samples",
                choices=caliData(session).samples(),
                options={
                    "maxItems": int(len(caliData(session).samples()) - 1),
                    "plugins": ["clear_button"],
                },
                selected=caliData(session).excludedSamples,
            )
            ui.update_selectize(
                "preprocessed_plot_xlabel_day",
                value=caliData(session).plotXlabelDay,
            )
        except Exception as e:
            print("preprocessed_load_state failed")
            print(e)

    @output(id="preprocessed_plot")
    @render_widget
    @reactive.event(preprocessed_update_toggle)
    def preprocessed_plot_wrapper():
        ### necessary for download fig
        return preprocessed_plot()

    def preprocessed_plot():
        print("preprocessed_plot")

        try:
            data = caliData(session).measurementFilteredGroupedDateTimeIndexed(
                input.preprocessed_current_measurement()
            )
            data_ungrouped = caliData(session).measurementFilteredDateTimeIndexed(
                input.preprocessed_current_measurement()
            )
            data_ungrouped = caliData(session).doGroupingByColumns(
                data_ungrouped, caliData(session).groupedBy
            )
    
            spans = getAreasWhereDatetimIndexIs(
                data,
                lambda x: not caliData(session).night > x.time() > caliData(session).day,
            )
            if caliData(session).groupedBy != "box":
                show_sem = True
            else:
                show_sem = False
            fig = calorimetryDataPlot(
                data,
                data_ungrouped,
                spans,
                add_sem=show_sem,
                xlabel_name=caliData(session).plotXlabelDay,
            )
            fig.update_layout(
                yaxis_title=input.preprocessed_current_measurement(),
                xaxis_title="Time",
                legend_title="",
                height=450,
            )
            return fig
        except Exception as e:
            print(f"Error in preprocessed_plot: {e}")
            return create_empty_plot("")

    @reactive.Effect
    @reactive.event(input.preprocessed_current_measurement)
    def currentMeasurement():
        print("preprocessed_setCurrentMeasurement")
        nonlocal preprocessed_measurement
        preprocessed_measurement = input.preprocessed_current_measurement()
        preprocessed_update()

    @reactive.Effect
    @reactive.event(input.preprocessed_grouped)
    def setGrouping():
        print("preprocessed_setGrouping")
        caliData(session).setGrouping(input.preprocessed_grouped())
        preprocessed_update()

    @reactive.Effect
    @reactive.event(input.preprocessed_excluded_samples)
    def setExcludedSamples():
        print("preprocessed_setExcludedSamples")
        try:
            caliData(session).setExcludedSamples(list(input.preprocessed_excluded_samples()))
            preprocessed_update()
        except:
            print("Error setting excluded samples")

    @reactive.Effect
    @reactive.event(input.preprocessed_all_same_day_start)
    def setAllSameDayStart():
        print("preprocessed_setAllSameDayStart")
        try:
            caliData(session).setAllSameDayStart(input.preprocessed_all_same_day_start())
            preprocessed_update()
        except:
            print("Error setting same day start")

    @reactive.Effect
    @reactive.event(input.preprocessed_plot_xlabel_day)
    def setPlotXlabelDay():
        print("preprocessed_setAllSameDayStart")
        try:
            caliData(session).setPlotXlabelDay(input.preprocessed_plot_xlabel_day())
            preprocessed_update()
        except:
            print("Error setting plot x label")

    @reactive.Effect
    @reactive.event(
        input.preprocessed_day_start_hour,
        input.preprocessed_day_start_minute,
        input.preprocessed_night_start_hour,
        input.preprocessed_night_start_minute,
    )
    def setNightAndDay():
        print("preprocessed_setNightAndDay")
        try:
            nightime = (
                str(input.preprocessed_night_start_hour())
                + ":"
                + str(input.preprocessed_night_start_minute())
            )
            print("nightime: " + nightime)
            night = datetime.datetime.strptime(nightime, "%H:%M").time()
            daytime = (
                str(input.preprocessed_day_start_hour())
                + ":"
                + str(input.preprocessed_day_start_minute())
            )
            print("daytime: " + daytime)
            day = datetime.datetime.strptime(daytime, "%H:%M").time()
            caliData(session).setNightAndDay(night, day)
            preprocessed_update()
        except:
            print("Error setting night and day")

    @reactive.Effect
    @reactive.event(
        input.preprocessed_measurement_start_date,
        input.preprocessed_measurement_start_time_hour,
        input.preprocessed_measurement_start_time_minute,
        input.preprocessed_measurement_end_date,
        input.preprocessed_measurement_end_time_hour,
        input.preprocessed_measurement_end_time_minute,
    )
    def croppData():
        print("preprocessed_croppData")
        try:
            start_date = str(input.preprocessed_measurement_start_date())
            start_time = (
                str(input.preprocessed_measurement_start_time_hour())
                + ":"
                + str(input.preprocessed_measurement_start_time_minute())
            )
            start = datetime.datetime.strptime(start_date + " " + start_time, "%Y-%m-%d %H:%M")
            print("start: " + str(start))
            end_date = str(input.preprocessed_measurement_end_date())
            end_time = (
                str(input.preprocessed_measurement_end_time_hour())
                + ":"
                + str(input.preprocessed_measurement_end_time_minute())
            )
            end = datetime.datetime.strptime(end_date + " " + end_time, "%Y-%m-%d %H:%M")
            print("end: " + str(end))
            maxEnd = caliData(session).data.index[-1]
            minStart = caliData(session).data.index[0]
            caliData(session).croppedStart = start if start > minStart else minStart
            caliData(session).croppedEnd = end if end < maxEnd else maxEnd
            preprocessed_update()
        except Exception as e:
            print("Error cropping data: " + str(e))

    @reactive.Effect
    @reactive.event(input.edit_grouping)
    def editGrouping():
        if caliData(session) is not None:
            print("Edit grouping")
            m = ui.modal(
                dialogEditAdditionalData_shiny,
                title="Table of phenotypic and conditional variables",
                footer=ui.div(
                    ui.modal_button("Cancel"),
                    ui.input_action_button("additionalData_confirm", "Confirm"),
                    class_="calopy-row",
                ),
                size="xl",
            )
            calopyStore(session).additionalData = pd.DataFrame(caliData(session).additionalData)
            additional_data_update()
            ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.additionalData_confirm)
    def confirm_additionalData():
        print("additionalData_confirm")
        new_additionalData: pd.DataFrame = calopyStore(session).additionalData
        if new_additionalData is not None:
            columns_index = 0
            for column in new_additionalData.columns:
                rows_index = 0
                for index, value in new_additionalData[column].items():
                    id = str(columns_index) + "_" + str(rows_index)
                    new_additionalData.at[index, column] = input[id]()
                    rows_index += 1
                columns_index += 1

            caliData(session).setAdditionalData(new_additionalData)
            ui.update_select(
                "preprocessed_grouped",
                choices=caliData(session).getCategoricalColumns(),
            )
        else:
            print("new_additionalData is None")
        ui.modal_remove(session)


    @reactive.Effect
    @reactive.event(input.edit_metabolic_variable)
    def editMetabolicVariable():
        if caliData(session) is not None:
            # Initialize the dialog controller
            dialogEditMetabolicVariable(input, output, session)
            metabolic_variable_update()  # <-- This triggers the dropdown update
            m = ui.modal(
                dialogEditMetabolicVariable_shiny,
                title="Edit Metabolic Variable",
                footer=ui.div(
                    ui.modal_button("Cancel"),
                    ui.input_action_button("metabolic_variable_confirm", "Confirm"),
                    class_="calopy-row",
                ),
                size="xl",
            )
            ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.metabolic_variable_confirm)
    def confirm_metabolic_variable():
        print("metabolic_variable_confirm")
        preprocessed_load_state()
        preprocessed_update()
        ui.modal_remove(session)

    @render.download(
        filename=lambda: f"{input.preprocessed_current_measurement()}-download-{datetime.datetime.now().isoformat('_','seconds')}.csv"
    )
    def preprocessed_data_downloader():
        print("downloadData")
        data = caliData(session).measurementFilteredGroupedDateTimeIndexed(
            input.preprocessed_current_measurement()
        )
        with io.BytesIO() as buf:
            data.to_csv(buf, sep=";", index=True)
            yield buf.getvalue()

    @render.download(
        filename=lambda: f"{input.preprocessed_current_measurement()}-download-plot-{datetime.datetime.now().isoformat('_','seconds')}.pdf"
    )
    def preprocessed_plot_downloader():
        print("downloadPlot")
        fig = preprocessed_plot()

        imb = fig.to_image(format="pdf", width=750, height=350, scale=1)
        buf = io.BytesIO(imb)
        buf.seek(0)
        return buf.getvalue(), "application/pdf"

        # with io.BytesIO() as buf:
        #     fig.write_image(buf, format="pdf")
        #     yield buf.getvalue()
