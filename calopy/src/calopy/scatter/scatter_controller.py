import datetime
import functools
import io

import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt
from shiny import reactive, render, ui
from shinywidgets import render_widget

from calopy.calopy_store import SCATTER_DAYSPLIT, SCATTER_FEATURE_NO_1, SCATTER_FEATURE_NO_2, \
                                SCATTER_GROUPED, SCATTER_MEASUREMENT_NO_1, \
                                SCATTER_MEASUREMENT_NO_2, SCATTER_START, caliData, caliState
from calopy.calopy_ui import SCATTER
from calopy.maths.features import FEATURE_FUNC_DICT, RAW_DATA, \
                                  get_input_selectize_feature_func_dict
from calopy.scatter.scatter_shiny import scatter_shiny
from calopy.shared_ui.plot_config import COLOR_DATECHANGE, COLOR_NIGHTTIME, get_color_samples
from calopy.shared_ui.scatterplot import createScatterplotFigure_new


def scatter(input, output, session):

    featureFunc_no_1 = FEATURE_FUNC_DICT[RAW_DATA]
    featureFunc_no_2 = FEATURE_FUNC_DICT[RAW_DATA]
    scatter_update_toggle = reactive.Value(True)
    data_measurement_no_1 = reactive.Value(None)
    data_measurement_no_2 = reactive.Value(None)

    def scatter_update():
        print("scatter_update_ui")
        scatter_update_toggle.set(not scatter_update_toggle())

    @output
    @render.ui
    def scatter_ui():
        print("scatter_ui")
        return scatter_shiny

    @reactive.Effect
    @reactive.event(input.selected_feature)
    def preprocessedSelectedFeature():
        print("scatter_selected_feature")
        if input.selected_feature() == SCATTER:
            load_state()
            scatter_update()

    def load_state():
        print("scatter_load_state")
        try:
            ui.update_select(
                "scatter_measurement_no_1",
                choices={
                    "measurements": {i: i for i in caliData(session).measurements()},
                    "---": {i: i for i in caliData(session).getContinuousColumns()},
                },
                selected=caliState(session)[SCATTER_MEASUREMENT_NO_1],
            )
            ui.update_select(
                "scatter_measurement_no_2",
                choices={
                    "measurements": {i: i for i in caliData(session).measurements()},
                    "---": {i: i for i in caliData(session).getContinuousColumns()},
                },
                selected=caliState(session)[SCATTER_MEASUREMENT_NO_2],
            )
            ui.update_select(
                "scatter_grouped",
                choices=caliData(session).getCategoricalColumns(),
                selected=caliState(session)[SCATTER_GROUPED],
            )
            ui.update_select(
                "scatter_feature_no_1",
                choices=get_input_selectize_feature_func_dict(),
                selected=caliState(session)[SCATTER_FEATURE_NO_1],
            )
            ui.update_select(
                "scatter_feature_no_2",
                choices=get_input_selectize_feature_func_dict(),
                selected=caliState(session)[SCATTER_FEATURE_NO_2],
            )
            ui.update_date("scatter_start_date", value=caliState(session)[SCATTER_START].date())
            ui.update_numeric(
                "scatter_start_time_hour",
                value=caliState(session)[SCATTER_START].time().hour,
            )
            ui.update_numeric(
                "scatter_start_time_minute",
                value=caliState(session)[SCATTER_START].time().minute,
            )
            ui.update_checkbox("scatter_daysplit", value=caliState(session)[SCATTER_DAYSPLIT])
        except Exception as e:
            print("load_state failed")
            print(e)

    @reactive.Effect
    @reactive.event(input.scatter_grouped)
    def setGrouping():
        print("scatter_setGrouping")
        grouping = input.scatter_grouped()
        caliData(session).setGrouping(grouping)
        caliState(session)[SCATTER_GROUPED] = grouping
        scatter_update()

    @reactive.Effect
    @reactive.event(input.scatter_measurement_no_1, input.scatter_measurement_no_2)
    def setMeasurements():
        print("scatter_setMeasurements")
        caliState(session)[SCATTER_MEASUREMENT_NO_1] = input.scatter_measurement_no_1()
        caliState(session)[SCATTER_MEASUREMENT_NO_2] = input.scatter_measurement_no_2()

        if (
            caliState(session)[SCATTER_MEASUREMENT_NO_1]
            in caliData(session).getContinuousColumns()
        ):
            ui.update_select("scatter_feature_no_1", choices=list(), selected=[])
        elif input.scatter_feature_no_1() is None:
            ui.update_select(
                "scatter_feature_no_1",
                choices=get_input_selectize_feature_func_dict(),
                selected=[RAW_DATA],
            )
        if (
            caliState(session)[SCATTER_MEASUREMENT_NO_2]
            in caliData(session).getContinuousColumns()
        ):
            ui.update_select("scatter_feature_no_2", choices=list(), selected=[])
        elif input.scatter_feature_no_2() is None:
            ui.update_select(
                "scatter_feature_no_2",
                choices=get_input_selectize_feature_func_dict(),
                selected=[RAW_DATA],
            )
        scatter_update()

    @reactive.Effect
    @reactive.event(input.scatter_feature_no_1)
    def setFeatureNo1():
        print(f"scatter_setFeatureNo1 {input.scatter_feature_no_1()}")
        caliState(session)[SCATTER_FEATURE_NO_1] = input.scatter_feature_no_1()
        nonlocal featureFunc_no_1
        featureFunc_no_1 = FEATURE_FUNC_DICT[caliState(session)[SCATTER_FEATURE_NO_1]]

        if input.scatter_measurement_no_1() in caliData(session).getContinuousColumns():
            ui.update_select("scatter_feature_no_1", choices=list(), selected=[])
            # ui.remove_ui(selector="div:has(> #scatter_feature_no_1)")
        else:
            if input.scatter_feature_no_1() == RAW_DATA:
                ui.update_checkbox("scatter_daysplit", value=False)
                ui.update_select(
                    "scatter_feature_no_2",
                    choices=get_input_selectize_feature_func_dict(),
                    selected=[RAW_DATA],
                )
            elif input.scatter_feature_no_2() == RAW_DATA:
                ui.update_select(
                    "scatter_feature_no_2",
                    choices=get_input_selectize_feature_func_dict(),
                    selected=[list(FEATURE_FUNC_DICT.keys())[1]],
                )
        scatter_update()

    @reactive.Effect
    @reactive.event(input.scatter_feature_no_2)
    def setFeatureNo2():
        print(f"scatter_setFeatureNo2 {input.scatter_feature_no_2()}")
        caliState(session)[SCATTER_FEATURE_NO_2] = input.scatter_feature_no_2()
        nonlocal featureFunc_no_2
        featureFunc_no_2 = FEATURE_FUNC_DICT[caliState(session)[SCATTER_FEATURE_NO_2]]

        if input.scatter_measurement_no_2() in caliData(session).getContinuousColumns():
            ui.update_select("scatter_feature_no_2", choices=list(), selected=[])
            # ui.remove_ui(selector="div:has(> #scatter_feature_no_2)")
        else:
            if input.scatter_feature_no_2() == RAW_DATA:
                ui.update_checkbox("scatter_daysplit", value=False)
                ui.update_select(
                    "scatter_feature_no_1",
                    choices=get_input_selectize_feature_func_dict(),
                    selected=[RAW_DATA],
                )
            elif input.scatter_feature_no_1() == RAW_DATA:
                ui.update_select(
                    "scatter_feature_no_1",
                    choices=get_input_selectize_feature_func_dict(),
                    selected=[list(FEATURE_FUNC_DICT.keys())[1]],
                )
        scatter_update()

    @reactive.Effect
    @reactive.event(input.scatter_daysplit)
    def setDaysplit():
        print("scatter_setDaysplit")
        caliState(session)[SCATTER_DAYSPLIT] = input.scatter_daysplit()
        scatter_update()

    @reactive.Effect
    @reactive.event(
        input.scatter_start_date,
        input.scatter_start_time_hour,
        input.scatter_start_time_minute,
    )
    def setScatterStart():
        print("scatter_setScatterStart")
        try:
            start_date = str(input.scatter_start_date())
            start_time = (
                str(input.scatter_start_time_hour()) + ":" + str(input.scatter_start_time_minute())
            )
            caliState(session)[SCATTER_START] = datetime.datetime.strptime(
                start_date + " " + start_time, "%Y-%m-%d %H:%M"
            )
            print("scatter_start: " + str(caliState(session)[SCATTER_START]))
            scatter_update()
        except Exception as e:
            print("Error setting start: " + str(e))

    @output
    @render.plot
    @reactive.event(data_measurement_no_1)
    def scatter_plot_measurement_1():
        fig, ax = plt.subplots()
        plot_df = data_measurement_no_1()
        color_palette = get_color_samples(plot_df.columns)
        plot_df.plot(ax=ax, color=[color_palette[col] for col in plot_df.columns], legend=None)
        ax.set_title(input.scatter_measurement_no_1())
        return fig

    @output
    @render.plot
    @reactive.event(data_measurement_no_2)
    def scatter_plot_measurement_2():
        fig, ax = plt.subplots()
        plot_df = data_measurement_no_2()
        color_palette = get_color_samples(plot_df.columns)
        plot_df.plot(ax=ax, color=[color_palette[col] for col in plot_df.columns], legend=None)
        ax.set_title(input.scatter_measurement_no_2())
        return fig

    @output
    @render.plot
    @reactive.event(scatter_update_toggle)
    def scatter_plot():
        print("scatter_plot")
        data_one = calculateByType(caliState(session)[SCATTER_MEASUREMENT_NO_1], featureFunc_no_1)
        data_two = calculateByType(caliState(session)[SCATTER_MEASUREMENT_NO_2], featureFunc_no_2)
        data_measurement_no_1.set(data_one)
        data_measurement_no_2.set(data_two)
        return createScatterplotFigure_new(
            data_one,
            data_two,
            input.scatter_measurement_no_1(),
            input.scatter_measurement_no_2(),
        )

    def calculateByType(selection, featureFunc):
        print("scatter_calculateByType:" + selection)
        data = None
        sessionData = caliData(session)

        if selection in sessionData.measurements():
            if not caliState(session)[SCATTER_DAYSPLIT]:
                data = featureFunc(sessionData.measurementFilteredDateTimeIndexed(selection))
            else:
                data = groupedByDate(
                    sessionData.measurementFilteredDateTimeIndexed(selection),
                    caliState(session)[SCATTER_START],
                ).agg(featureFunc)
        else:
            data = sessionData.getContinuousColumnIndexedByBox(selection)

        if type(data) is pd.Series:
            data = data.to_frame()
            grouping = caliState(session)[SCATTER_GROUPED]
            if grouping != "box":
                print(f"grouped by {grouping}")
                data = sessionData.doGroupingByIndex(data, grouping)
        else:
            data = sessionData.doGrouping(data, caliState(session)[SCATTER_GROUPED])
        return data

    @output
    @render_widget
    @reactive.event(scatter_update_toggle)
    def scatter_show_daysplit():
        data = caliData(session).measurementFilteredGroupedDateTimeIndexed(
            caliState(session)[SCATTER_MEASUREMENT_NO_1]
        )

        fig = px.line(data)
        dayChangeStart = caliState(session)[SCATTER_START]
        index_of_day_change = []
        while dayChangeStart < data.index[-1]:
            index_of_day_change.append(dayChangeStart)
            dayChangeStart += datetime.timedelta(days=1)
        for daychange in index_of_day_change:
            fig.add_vline(
                x=daychange,
                line_width=2,
                line_dash="dash",
                line_color=COLOR_DATECHANGE,
                opacity=1,
                layer="below",
            )
        fig.add_vrect(
            x0=index_of_day_change[0],
            x1=index_of_day_change[-1],
            fillcolor=COLOR_NIGHTTIME,
            line_width=0,
            layer="below",
            opacity=1,
        )
        return fig

    @render.download(
        filename=lambda: f"scatter-download-{datetime.datetime.now().isoformat()}.csv"
    )
    def scatter_data_downloader():
        print("scatter downloadData")
        data = {}
        data_one = data_measurement_no_1()
        data_two = data_measurement_no_2()
        key_first_column = input.scatter_measurement_no_1()
        for label, content in data_one.items():
            _one, _two = data_one[label], data_two[label]
            _one.name = key_first_column
            _two.name = input.scatter_measurement_no_2()
            data[label] = pd.concat([_one, _two], axis=1).sort_values(key_first_column, axis=0)
        print(data)
        with io.BytesIO() as buf:
            pd.concat(data).to_csv(buf, sep=";", index=True)
            yield buf.getvalue()


def groupedByDate(dataframe, start):
    print("scatter_groupedByDate")
    days_column_name = "date"
    dataframe[days_column_name] = dataframe.index
    # apply function to the date column and replace the date with the number of days between the value and scatter_start
    dataframe[days_column_name] = dataframe[days_column_name].apply(
        lambda x: f"day_{(x - start).days}"
    )
    # remove all rows of the dataframe where index is before scatter_start
    dataframe = dataframe[dataframe.index >= start]

    days_set = getOrderedListOfDays(dataframe, days_column_name)
    # find the first and the last entry in the dataframe for the last day
    lastDay = days_set[-1]
    first = dataframe[dataframe[days_column_name] == lastDay].index[0]
    last = dataframe[dataframe[days_column_name] == lastDay].index[-1]
    # remove al rows of the day if the difference between the first set and the last entry is mor than 1410 minutes (23,5 hours)
    if (last - first).seconds < 1410 * 60:
        dataframe = dataframe[dataframe[days_column_name] != lastDay]

    dataframe = dataframe.groupby(days_column_name)
    return dataframe


def getOrderedListOfDays(dataframe, days_column_name):
    days_set = [dataframe[days_column_name][0]]
    for day in dataframe[days_column_name]:
        if day != days_set[-1]:
            days_set.append(day)
    return days_set
