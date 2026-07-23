import datetime
import io


import pandas as pd
import pingouin
from matplotlib import pyplot as plt
from pandas.core.indexers.objects import FixedForwardWindowIndexer
from shiny import reactive, render, ui
from shinywidgets import render_widget

from calopy.calopy_store import WINDOW_DAY_NIGHT_RESTRICTIONS, WINDOW_MEASUREMENT_NO_1, \
                                WINDOW_OVERLAPPING_WINDOWS, WINDOW_SIZE, WINDOW_STAT_ANNOTATIONS, \
                                WINDOW_SWARMPLOT, WINDOW_TIME_STEPS_MOVED_BY, caliData, \
                                caliState
from calopy.calopy_ui import WINDOW
from calopy.maths.filter.NightAndDayFilter import NightAndDayFilter
from calopy.maths.series_utils import getAreasWhereDatetimIndexIs, getIndexOf24HourInterval
from calopy.shared_ui.boxplot import addStatsAnnotationtoWindowedBoxPlot, binnedWindowsBoxPlot
from calopy.shared_ui.plot_config import create_empty_plot
from calopy.window.window_shiny import ALL_SAMPLE_WINDOW, NEXT_SEGMENTS, ROLLING_WINDOW, \
                                       window_analysis_shiny

NONE = "none"
DAY_ONLY = "day only"
NIGHT_ONLY = "night only"


def window_analysis(input, output, session):
    window_update_toggle = reactive.Value(True)
    stat_result = reactive.Value(None)
    windowed_data = None

    def rollingWindow(data):
        print("nextSegment")
        indexer = FixedForwardWindowIndexer(window_size=input.window_size())
        if input.overlapping_windows():
            steps_to_move = input.timesteps_moved_by()
        else:
            steps_to_move = input.window_size()
        return data.rolling(indexer, step=steps_to_move).mean()

    def window_update():
        print("window_update_ui")
        window_update_toggle.set(not window_update_toggle())

    @output
    @render.ui
    def window_ui():
        print("window_ui")
        return window_analysis_shiny

    @reactive.Effect
    @reactive.event(input.selected_feature)
    def preprocessedSelectedFeature():
        print("selected_feature")
        if input.selected_feature() == WINDOW:
            load_state()
            window_update()

    def load_state():
        print("load_state")
        try:
            ui.update_select(
                "window_grouped",
                choices=caliData(session).getCategoricalColumns(),
                selected=caliData(session).groupedBy,
            )
            ui.update_select(
                "window_measurement_no_1",
                choices=caliData(session).measurements(),
                selected=caliState(session)[WINDOW_MEASUREMENT_NO_1],
            )
            ui.update_checkbox("window_swarmplot", value=caliState(session)[WINDOW_SWARMPLOT])
            ui.update_checkbox(
                "window_stat_annotations",
                value=caliState(session)[WINDOW_STAT_ANNOTATIONS],
            )
            ui.update_checkbox(
                "overlapping_windows",
                value=caliState(session)[WINDOW_OVERLAPPING_WINDOWS],
            )
            ui.update_select(
                "day_night_restrictions",
                choices=[NONE, DAY_ONLY, NIGHT_ONLY],
                selected=caliState(session)[WINDOW_DAY_NIGHT_RESTRICTIONS],
            )
            ui.update_numeric("window_size", value=caliState(session)[WINDOW_SIZE])
            ui.update_numeric(
                "timesteps_moved_by",
                value=caliState(session)[WINDOW_TIME_STEPS_MOVED_BY],
            )
        except Exception as e:
            print("load_state failed")
            print(e)

    @reactive.Effect
    @reactive.event(input.window_grouped)
    def setGrouping():
        print("set Grouping")
        if caliState(session) is not None:
            caliData(session).setGrouping(input.window_grouped())
            window_update()

    @reactive.Effect
    @reactive.event(input.window_measurement_no_1)
    def setMeasurements():
        print("setMeasurements")
        if caliState(session) is not None:
            caliState(session)[WINDOW_MEASUREMENT_NO_1] = input.window_measurement_no_1()
            window_update()

    @reactive.Effect
    @reactive.event(input.day_night_restrictions)
    def setDaytimeRestrictions():
        if caliState(session) is not None:
            caliState(session)[WINDOW_DAY_NIGHT_RESTRICTIONS] = input.day_night_restrictions()
            window_update()

    @reactive.Effect
    @reactive.event(input.overlapping_windows)
    def setOverlappingWindows():
        if caliState(session) is not None:
            caliState(session)[WINDOW_OVERLAPPING_WINDOWS] = input.overlapping_windows()
            window_update()

    @reactive.Effect
    @reactive.event(input.window_size, input.timesteps_moved_by)
    def setWindowSizes():
        if caliState(session) is not None:
            caliState(session)[WINDOW_SIZE] = input.window_size()
            caliState(session)[WINDOW_TIME_STEPS_MOVED_BY] = input.timesteps_moved_by()
            window_update()

    @reactive.Effect
    @reactive.event(input.window_swarmplot, input.window_stat_annotations)
    def setMethod():
        if caliState(session) is not None:
            caliState(session)[WINDOW_SWARMPLOT] = input.window_swarmplot()
            caliState(session)[WINDOW_STAT_ANNOTATIONS] = input.window_stat_annotations()
            window_update()

    def get_windowed_data(data, value_name):
        windowed_data = rollingWindow(data)
        windowed_data.reset_index(inplace=True)
        windowed_data.rename(columns={"index": "bin"}, inplace=True)
        # windowed_data_long = pd.melt(windowed_data, id_vars=['bin'], var_name='box', value_name='value')
        windowed_data_long = pd.melt(
            windowed_data, id_vars=["datetime"], var_name="box", value_name="value"
        )
        windowed_data_long["value_name"] = value_name
        addData = caliData(session).additionalData[["box", caliData(session).groupedBy]]
        addData.columns.values[1] = "group"
        windowed_data = pd.merge(windowed_data_long, addData, on="box")
        return windowed_data

    @output(id="window_plot")
    @render_widget
    @reactive.event(window_update_toggle)
    def window_plot_wrapper():
        return window_plot()

    def window_plot():
        print("window_plot")
        try:
            nonlocal windowed_data
            data = caliData(session).measurementFilteredDateTimeIndexed(
                input.window_measurement_no_1()
            )
    
            spans = getAreasWhereDatetimIndexIs(
                data,
                lambda x: not caliData(session).night > x.time() > caliData(session).day,
            )
    
            if caliData(session).plotXlabelDay == "day":
                ### make all files start on 1st january to show day 1 instead of exact date in plot
                days_difference = (pd.Timestamp("2018-01-01").date() - data.index[0].date()).days -1
                data.index = data.index + pd.DateOffset(days=days_difference)
                spans = [
                    (
                        start + pd.DateOffset(days=days_difference),
                        end + pd.DateOffset(days=days_difference),
                    )
                    for start, end in spans
                ]

    
            day_night_restrictions = caliState(session)[WINDOW_DAY_NIGHT_RESTRICTIONS]
            if day_night_restrictions == DAY_ONLY:
                data = NightAndDayFilter(caliData(session).night, caliData(session).day).apply(data)[
                    NightAndDayFilter.DAY
                ]
            if day_night_restrictions == NIGHT_ONLY:
                data = NightAndDayFilter(caliData(session).night, caliData(session).day).apply(data)[
                    NightAndDayFilter.NIGHT
                ]
            windowed_data = get_windowed_data(data, input.window_measurement_no_1())
            # stat_result.set(boxPlot_window(ax, windowed_data, doSwarmPlot, doStatAnnotations))
    
            doSwarmPlot = input.window_swarmplot()
            doStatAnnotations = input.window_stat_annotations()
    
            fig = binnedWindowsBoxPlot(windowed_data, spans, x="datetime", do_swarm=doSwarmPlot)
    
            if input.window_grouped() != "box":
                stat_result.set(windowStatistics(windowed_data))
                if doStatAnnotations:
                    fig = addStatsAnnotationtoWindowedBoxPlot(
                        fig, stat_result(), y_max=windowed_data["value"].max() * 1.03
                    )
            else:
                stat_result.set(None)
    
            fig.update_layout(
                template="simple_white",
                title="",
                xaxis_title="Time",
                yaxis_title=input.window_measurement_no_1(),
            )
            
            if caliData(session).plotXlabelDay == "day":
                fig.update_xaxes(tickformat="%H:%M\nDay %_j")  ### show day 1 instead of exact date
            
            return fig
        except Exception as e:
            print(f"Error in window_plot: {e}")
            return create_empty_plot("")


    def windowStatistics(data):
        results_df = pd.DataFrame()

        for timepoint, subset in data.groupby("datetime"):
            if subset["group"].nunique() > 1:
                aov = pingouin.anova(dv="value", between="group", data=subset, detailed=True)
                # Add a column for the datetime
                group_effect = aov[aov["Source"] == "group"].copy()
                # Add a column for the datetime
                group_effect["datetime"] = timepoint
                # Append the filtered result to the results dataframe
                results_df = pd.concat([results_df, group_effect], ignore_index=True)
            else:
                print(f"Not enough groups for ANOVA at timepoint {timepoint}.")

        columns_order = ["datetime"] + [col for col in results_df.columns if col != "datetime"]
        results_df = results_df[columns_order]

        reject, p_fdr = pingouin.multicomp(results_df["p-unc"], alpha=0.05, method="fdr_bh")
        results_df["p-fdr"] = p_fdr.tolist()

        return results_df

    @output
    @render.table
    @reactive.event(window_update_toggle)
    def window_stat_annotations_table():
        return stat_result()

    @output
    @render.text
    def window_stats_summary():
        textout = (
            "Statistics was done using Pingouin[1] "
            f"(v{pingouin.__version__}) "
            "'ANOVA' function with between factor = 'group'. \np-Values were adjusted for multiple testing using Benjamini/Hochberg FDR correction using Pingouin multicomp function."
            "\n\n[1] Vallat, R. (2018). Pingouin: statistics in Python. Journal of Open Source Software, 3(31), 1026, \nhttps://doi.org/10.21105/joss.01026"
        )
        return textout

    @render.download(
        filename=lambda: f"{input.window_measurement_no_1()}-window-download-{datetime.datetime.now().isoformat()}.csv"
    )
    def windows_data_downloader():
        print("downloadData")
        nonlocal windowed_data
        with io.BytesIO() as buf:
            windowed_data.to_csv(buf, sep=",", index=True)
            yield buf.getvalue()

    @render.download(
        filename=lambda: f"{input.window_measurement_no_1()}-window-stats-{datetime.datetime.now().isoformat()}.csv"
    )
    def window_stats_downloader():
        print("download stats")
        with io.BytesIO() as buf:
            stat_result().to_csv(buf, sep=",", index=True)
            yield buf.getvalue()

    @render.download(
        filename=lambda: f"{input.window_measurement_no_1()}-window-download-{datetime.datetime.now().isoformat()}.pdf"
    )
    def windows_plot_downloader():
        print("downloadPlot")
        fig = window_plot()

        if fig is None:
            return "", "application/pdf"  # Return an empty response if no figure
        try:
            imb = fig.to_image(format="pdf", width=750, height=350, scale=1)
            buf = io.BytesIO(imb)
            buf.seek(0)
            return buf.getvalue(), "application/pdf"
        except:
            pass

        # fd, path = tempfile.mkstemp(suffix = '.pdf')
        # fig.savefig(path)
        # return path
