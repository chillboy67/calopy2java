import datetime
import io

import pandas as pd
import pingouin

from shiny import reactive, render, ui
from shinywidgets import render_widget

from calopy.calopy_store import CONDITIONS_CONDITIONS, CONDITIONS_FEATURE, CONDITIONS_GROUPED, \
                                CONDITIONS_MEASUREMENT, caliData, caliState, calopyStore
from calopy.calopy_ui import CONDITIONS
from calopy.conditions.conditions_shiny import conditions_shiny
from calopy.conditions.conditions_statistics import mixed_anova_statistics, \
                                                    paired_ttest_statistics, rm_anova_statistics
from calopy.conditions.DialogConditions import dialog_conditions_update, dialogConditions_shiny
from calopy.maths.features import FEATURE_FUNC_DICT
from calopy.maths.series_utils import getAreasWhereDatetimIndexIs, getIndexOf24HourInterval
from calopy.shared_ui.ICdataPlot import calorimetryDataPlot, conditionsStatsPlot
from calopy.shared_ui.plot_config import COLOR_DATECHANGE, COLOR_NIGHTTIME, get_color_samples, create_empty_plot
from calopy.shared_ui.spans import displaySpan, displaySpansWidget

TO = "to"
FROM = "from"
TEXT = "Condition"
CONDITION = "condition"
FEATURE = "feature"
SAMPLE = "sample"
GROUP = "group"


def conditions(input, output, session):

    conditions_update_toggle = reactive.Value(True)
    slicedData = reactive.Value(pd.DataFrame)
    featureFunc = FEATURE_FUNC_DICT[list(FEATURE_FUNC_DICT.keys())[1]]
    stat_result = reactive.Value(None)

    def conditions_update():
        print("conditions_update")
        conditions_update_toggle.set(not conditions_update_toggle())

    @output
    @render.ui
    def conditions_ui():
        print("conditions_ui")
        try:
            ### start with two conditions if not initialized
            if not caliState(session)[CONDITIONS_CONDITIONS]:
                condition_start = caliData(session).croppedStart
                condition_end = caliData(session).croppedEnd
                condition_mid = condition_start + (condition_end - condition_start) / 2
                
                caliState(session)[CONDITIONS_CONDITIONS] = [
                    {TEXT: "Condition1", FROM: condition_start, TO: condition_mid},
                    {TEXT: "Condition2", FROM: condition_mid, TO: condition_end},
                ]
        except:
            pass
        return conditions_shiny

    @reactive.Effect
    @reactive.event(input.selected_feature)
    def preprocessedSelectedFeature():
        print("selected_feature")
        if input.selected_feature() == CONDITIONS:
            load_state()
            conditions_update()

    def load_state():
        print("load_state")
        try:
            ui.update_select(
                "conditions_grouped",
                choices=caliData(session).getCategoricalColumns(),
                selected=caliData(session).groupedBy,
            )
            ui.update_select(
                "conditions_measurement",
                choices=caliData(session).measurements(),
                selected=caliState(session)[CONDITIONS_MEASUREMENT],
            )
        except Exception as e:
            print("load_state failed")
            print(e)

    @reactive.Effect
    @reactive.event(input.conditions_grouped)
    def setGrouping():
        print("setGrouping")
        if caliData(session) is not None:
            caliData(session).setGrouping(input.conditions_grouped())
            caliState(session)[CONDITIONS_GROUPED] = input.conditions_grouped()
            conditions_update()

    @reactive.Effect
    @reactive.event(input.conditions_measurement)
    def setMeasurements():
        print("setMeasurements")
        if caliState(session) is not None:
            caliState(session)[CONDITIONS_MEASUREMENT] = input.conditions_measurement()
            conditions_update()

    @reactive.Effect
    @reactive.event(input.conditions_feature)
    def setFeature():
        print("setFeature")
        if caliState(session) is not None:
            caliState(session)[CONDITIONS_FEATURE] = input.conditions_feature()
            nonlocal featureFunc
            featureFunc = FEATURE_FUNC_DICT[caliState(session)[CONDITIONS_FEATURE]]
            conditions_update()

    @output(id="between_conditions_data_plot")
    @render_widget
    @reactive.event(conditions_update_toggle)
    def between_conditions_data_plot_wrapper():
        ### necessary for download fig
        return between_conditions_data_plot()

    def between_conditions_data_plot():
        print("new conditions_plot")
        try:
            data = caliData(session).measurementFilteredGroupedDateTimeIndexed(
                caliState(session)[CONDITIONS_MEASUREMENT]
            )
    
            data_ungrouped = caliData(session).measurementFilteredDateTimeIndexed(
                input.conditions_measurement()
            )
            data_ungrouped = caliData(session).doGroupingByColumns(
                data_ungrouped, caliData(session).groupedBy
            )
    
            all_conditions = caliState(session)[CONDITIONS_CONDITIONS]
    
            ### keep before calorimetryDataPlot - set daystart to day 1
            if caliData(session).plotXlabelDay == "day":
                days_difference = (pd.Timestamp("2018-01-01").date() - data.index[0].date()).days -1
                all_conditions = [
                    {
                        TEXT: entry[TEXT],
                        FROM: entry[FROM] + pd.DateOffset(days=days_difference),
                        TO: entry[TO] + pd.DateOffset(days=days_difference),
                    }
                    for entry in all_conditions
                ]
    
            show_peaks_feature_df = (
                featureFunc(data_ungrouped) if input.conditions_showpeak() else None
            )
            fig = calorimetryDataPlot(
                data,
                data_ungrouped,
                getAreasWhereDatetimIndexIs(
                    data,
                    lambda x: not caliData(session).night > x.time() > caliData(session).day,
                ),
                add_feature_peaks=input.conditions_showpeak(),
                feature_df=show_peaks_feature_df,
                add_sem=input.conditions_show_SEM(),
                xlabel_name=caliData(session).plotXlabelDay,
            )
    
            displaySpansWidget(
                fig, map(lambda condition: (condition[FROM], condition[TO]), all_conditions)
            )
            fig.update_layout(
                yaxis_title=input.conditions_measurement(),
                xaxis_title="Time",
                legend_title="",
                height=450,
            )
            return fig
        except Exception as e:
            print(f"Error in between_conditions_data_plot: {e}")
            return create_empty_plot("")


    @reactive.Effect
    @reactive.event(conditions_update_toggle)
    def compute_sliced_data():
        print("compute_sliced_data")
        data = caliData(session)
        if data is not None:
            # Old
            # slicedData.set(sliceByCondition(data.measurementFilteredGroupedDateTimeIndexed(input.conditions_measurement())))
            # New
            data_ungrouped = data.measurementFilteredDateTimeIndexed(
                input.conditions_measurement()
            )
            data_ungrouped = data.doGroupingByColumns(data_ungrouped, caliData(session).groupedBy)
            slicedData.set(sliceByCondition(data_ungrouped))

    @output
    @render_widget
    @reactive.event(slicedData)
    def conditions_plot():
        try:
            group_order = (
                caliData(session)
                .measurementFilteredGroupedDateTimeIndexed(caliState(session)[CONDITIONS_MEASUREMENT])
                .columns
            )
            fig = conditionsStatsPlot(slicedData(), group_order,
                                      dependent_var=caliState(session)[CONDITIONS_MEASUREMENT],
                                      dependent_feature=caliState(session)[CONDITIONS_FEATURE])
            return fig
        except Exception as e:
            print(f"Error in conditions_plot: {e}")
            return create_empty_plot("")

    def sliceByCondition(data):
        outDF = pd.DataFrame(columns=[SAMPLE, FEATURE, CONDITION, GROUP])
        for condition in caliState(session)[CONDITIONS_CONDITIONS]:
            dataDict = {}
            feature_df = featureFunc(
                data[(data.index > condition[FROM]) & (data.index <= condition[TO])]
            )
            dataDict[FEATURE] = feature_df["value"]
            dataDict[CONDITION] = condition[TEXT]
            dataDict[SAMPLE] = feature_df["box"]
            dataDict[GROUP] = feature_df["group"]

            outDF = pd.concat([outDF, pd.DataFrame(dataDict)], ignore_index=True)

        return outDF

    @output
    @render.table
    @reactive.event(conditions_update_toggle)
    def conditions_list():
        if caliState(session) is not None:
            return pd.DataFrame(caliState(session)[CONDITIONS_CONDITIONS])
        else:
            return pd.DataFrame()

    @reactive.Effect
    @reactive.event(input.conditions_edit)
    def conditions_edit():
        if caliState(session) is not None:
            m = ui.modal(
                dialogConditions_shiny,
                title="Edit conditions",
                footer=ui.div(
                    ui.modal_button("Cancel"),
                    ui.input_action_button("conditions_confirm", "Confirm"),
                    class_="calopy-row",
                ),
                size="m",
            )
            dialog_conditions_update()
            ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.conditions_confirm)
    def conditions_confirm():
        print("update_conditions_entries")
        try:
            for i, condition in enumerate(caliState(session)[CONDITIONS_CONDITIONS]):
                condition[TEXT] = input["conditions_text_" + str(i)]()
                start_date = str(input["conditions_start_date_" + str(i)]())
                start_time = (
                    str(input["conditions_start_time_hour_" + str(i)]())
                    + ":"
                    + str(input["conditions_start_time_minute_" + str(i)]())
                )
                start = datetime.datetime.strptime(start_date + " " + start_time, "%Y-%m-%d %H:%M")
                condition[FROM] = start
                end_date = str(input["conditions_end_date_" + str(i)]())
                end_time = (
                    str(input["conditions_end_time_hour_" + str(i)]())
                    + ":"
                    + str(input["conditions_end_time_minute_" + str(i)]())
                )
                end = datetime.datetime.strptime(end_date + " " + end_time, "%Y-%m-%d %H:%M")
                condition[TO] = end
        except:
            pass
        ui.modal_remove(session)
        conditions_update()

    @output
    @render.download(
        filename=lambda: f"temporalconditions_plot-{datetime.datetime.now().isoformat('_','seconds')}.pdf"
    )
    def conditions_plot1_downloader():
        fig = between_conditions_data_plot()
        if fig is None:
            return "", "application/pdf"  # Return an empty response if no figure
        try:
            imb = fig.to_image(format="pdf", width=750, height=350, scale=1)
            buf = io.BytesIO(imb)
            buf.seek(0)
            return buf.getvalue(), "application/pdf"
        except:
            pass

    @output
    @render.download(
        filename=lambda: f"temporalconditions_data-{datetime.datetime.now().isoformat('_','seconds')}.csv"
    )
    def conditions_data1_downloader():
        data = caliData(session).measurementFilteredGroupedDateTimeIndexed(
            caliState(session)[CONDITIONS_MEASUREMENT]
        )
        with io.BytesIO() as buf:
            data.to_csv(buf, sep=";", index=True)
            yield buf.getvalue()
        

    @output
    @render.download(
        filename=lambda: f"slicedData-{datetime.datetime.now().isoformat('_', 'seconds')}.pdf"
    )
    def conditions_stats_plot_downloader():
        group_order = (
            caliData(session)
            .measurementFilteredGroupedDateTimeIndexed(caliState(session)[CONDITIONS_MEASUREMENT])
            .columns
        )
        fig = conditionsStatsPlot(slicedData(), group_order)
        if fig is None:
            return "", "application/pdf"  # Return an empty response if no figure
        try:
            imb = fig.to_image(format="pdf", width=750, height=350, scale=1)
            buf = io.BytesIO(imb)
            buf.seek(0)
            return buf.getvalue(), "application/pdf"
        except:
            pass

    @render.download(
        filename=lambda: f"slicedData-{datetime.datetime.now().isoformat('_','seconds')}.csv"
    )
    def condition_sliced_data_download():
        with io.BytesIO() as buf:
            slicedData().to_csv(buf, sep=",", index=False)
            yield buf.getvalue()

    @render.download(
        filename=lambda: f"{input.conditions_measurement()}-condition-stats-{datetime.datetime.now().isoformat()}.csv"
    )
    def condition_stats_downloader():
        print("download stats")
        with io.BytesIO() as buf:
            stat_result().to_csv(buf, sep=",", index=True)
            yield buf.getvalue()

    @output
    @render.table
    def conditions_stat_result():
        data = slicedData()
        # no aggregation -> do ttest
        try:
            if input.conditions_grouped() == "box":
                stat_result.set(paired_ttest_statistics(data))
                return stat_result()
            else:  # input.paired_ttest_results():
                stat_result.set(mixed_anova_statistics(data))
                return stat_result()
        except Exception as e:
            print("conditions_stat_result failed")
            print(e)
            return None

    @output
    @render.text
    def conditions_stats_summary():
        if input.conditions_grouped() == "box":
            textout = (
                "Statistics was done using Pingouin[1] "
                f"(v{pingouin.__version__}) "
                "'pairwise_tests' function with \n within-subject factor='condition' and subject identifier ='box_id'. "
                "\n\n[1] Vallat, R. (2018). Pingouin: statistics in Python. Journal of Open Source Software, 3(31), 1026, \nhttps://doi.org/10.21105/joss.01026"
            )

            return textout
        else:  # input.paired_ttest_results():
            textout = (
                "Statistics was done using Pingouin[1] "
                f"(v{pingouin.__version__}) "
                "'mixed_anova' function with \n within-subject factor='condition', subject identifier ='box_id' and  between factor = "
                f"{input.conditions_grouped()} "
                "\n\n[1] Vallat, R. (2018). Pingouin: statistics in Python. Journal of Open Source Software, 3(31), 1026, \nhttps://doi.org/10.21105/joss.01026"
            )
            return textout

    @reactive.Effect
    @reactive.event(input.conditions_show_SEM, input.conditions_showpeak)
    def handleCheckboxChanges():
        conditions_update()
