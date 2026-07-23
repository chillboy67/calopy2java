import matplotlib
from matplotlib import pyplot as plt

matplotlib.use("agg")
import datetime
import io
import re

import pandas as pd
import pingouin
import statsmodels
import plotly.express as px
import plotly.graph_objects as go

from shiny import reactive, render, ui
from shinywidgets import render_widget

from calopy.between_groups.between_groups_shiny import between_groups_shiny
from calopy.calopy_store import caliData, caliState, BETWEEN_GROUPS_MEASUREMENT_1, BETWEEN_GROUPS_MEASUREMENT_2, \
                        BETWEEN_GROUPS_FEATURE_FUNC_VAR1, BETWEEN_GROUPS_FEATURE_FUNC_VAR2, \
                        BETWEEN_GROUPS_LIGHT_DARK_FILTER, BETWEEN_GROUPS_GROUPING_1, BETWEEN_GROUPS_GROUPING_2, \
                        BETWEEN_GROUPS_USE_WELCH, BETWEEN_GROUPS_USE_2WAY_ANOVA, \
                        BETWEEN_GROUPS_COMPARE_LIGHT_DARK, BETWEEN_GROUPS_USE_COVARIATE

from calopy.calopy_ui import BETWEENGROUPS
from calopy.maths.features import FEATURE_FUNC_DICT, MEAN, RAW_DATA, \
                                  get_input_selectize_feature_func_dict
from calopy.maths.filter.NightAndDayFilter import NightAndDayFilter
from calopy.maths.series_utils import getAreasWhereDatetimIndexIs
from calopy.maths.statistic import anova, calopy_ancova, calopy_regression, \
                                  calopy_ancova_full_model
from calopy.shared_ui.boxplot import boxPlot_Betweengroups
from calopy.shared_ui.ICdataPlot import calorimetryDataPlot
from calopy.shared_ui.plot_config import create_empty_plot
from calopy.shared_ui.scatterplot import between_groups_regression_plot

def between_groups(input, output, session):
    feature_func_var1 = FEATURE_FUNC_DICT[RAW_DATA]
    feature_func_var2 = FEATURE_FUNC_DICT[MEAN]
    between_groups_update_toggle = reactive.Value(True)
    between_groups_measurement_no_1 = None
    between_groups_measurement_no_2 = None
    between_groups_grouped = None
    between_groups_2way_factor = None
    raw_feature = None
    raw_feature2 = None
    stat_result = reactive.Value(None)

    def between_groups_update():
        print("between_groups_update_ui")
        between_groups_update_toggle.set(not between_groups_update_toggle())

    @output
    @render.ui
    def between_groups_ui():
        print("between_groups_ui")
        return between_groups_shiny

    @reactive.Effect
    @reactive.event(input.selected_feature)
    def preprocessedSelectedFeature():
        print("selected_feature")
        if input.selected_feature() == BETWEENGROUPS:
            load_state()
            between_groups_update()

    def load_state():
        print("load_state")
        try:
            cali_data = caliData(session)
            choices_grouping = cali_data.getCategoricalColumns()

            ui.update_select(
                "between_groups_grouped",
                choices=cali_data.getCategoricalColumns(),
                selected=between_groups_grouped,
            )

            measurement_choices = cali_data.measurements()
            ui.update_select(
                "between_groups_measurement_no_1",
                choices=measurement_choices + caliData(session).getContinuousColumns(),
                selected=between_groups_measurement_no_1,
            )

            ui.update_select(
                "raw_feature",
                choices=get_input_selectize_feature_func_dict(),
                selected=raw_feature,
            )
            ui.update_select(
                "raw_feature2",
                choices=get_input_selectize_feature_func_dict(remove_raw_data=True),
                selected=raw_feature2,
            )

            ui.update_select(
                "between_groups_2way_factor",
                choices=choices_grouping,
                selected=between_groups_2way_factor,
            )

            ui.update_select(
                "between_groups_measurement_no_2",
                choices=measurement_choices + caliData(session).getContinuousColumns(),
                selected=between_groups_measurement_no_2,
            )

        except Exception as e:
            print("load_state failed")
            print(e)

    @reactive.Effect
    @reactive.event(input.between_groups_grouped, input.between_groups_2way_factor)
    def setGrouping():
        print("setGrouping")
        if caliData(session) is not None:
            caliData(session).setGrouping(input.between_groups_grouped())
            nonlocal between_groups_grouped
            between_groups_grouped = input.between_groups_grouped()
            caliState(session)[BETWEEN_GROUPS_GROUPING_1] = input.between_groups_grouped()
            caliState(session)[BETWEEN_GROUPS_GROUPING_2] = input.between_groups_2way_factor()
            between_groups_update()

    @reactive.Effect
    @reactive.event(input.between_groups_measurement_no_1, input.between_groups_measurement_no_2)
    def setMeasurements():
        print("setMeasurements")
        nonlocal between_groups_measurement_no_1
        nonlocal between_groups_measurement_no_2
        between_groups_measurement_no_1 = input.between_groups_measurement_no_1()
        between_groups_measurement_no_2 = input.between_groups_measurement_no_2()
        caliState(session)[BETWEEN_GROUPS_MEASUREMENT_1] = input.between_groups_measurement_no_1()
        caliState(session)[BETWEEN_GROUPS_MEASUREMENT_2] = input.between_groups_measurement_no_2()
        between_groups_update()

    @reactive.Effect
    @reactive.event(input.raw_feature, input.raw_feature2)
    def setFeature():
        print("setFeature")
        nonlocal feature_func_var1
        nonlocal feature_func_var2
        feature_func_var1 = FEATURE_FUNC_DICT[input.raw_feature()]
        feature_func_var2 = FEATURE_FUNC_DICT[input.raw_feature2()]
        caliState(session)[BETWEEN_GROUPS_FEATURE_FUNC_VAR1] = input.raw_feature()
        caliState(session)[BETWEEN_GROUPS_FEATURE_FUNC_VAR2] = input.raw_feature2()
        between_groups_update()

    @reactive.Effect
    @reactive.event(input.light_dark_selection)
    def setPhaseFilter():
        if caliData(session) is not None:
            caliState(session)[BETWEEN_GROUPS_LIGHT_DARK_FILTER] = input.light_dark_selection()
            between_groups_update()

    @reactive.Effect
    @reactive.event(
        input.use_welch,
        input.use_2wayfactor,
        input.between_groups_night_and_day,
        input.use_covariable)
    def setOptions():
        if caliData(session) is not None:
            caliState(session)[BETWEEN_GROUPS_USE_WELCH] = input.use_welch()
            caliState(session)[BETWEEN_GROUPS_USE_2WAY_ANOVA] = input.use_2wayfactor()
            caliState(session)[BETWEEN_GROUPS_COMPARE_LIGHT_DARK] = input.between_groups_night_and_day()
            caliState(session)[BETWEEN_GROUPS_USE_COVARIATE] = input.use_covariable()
            between_groups_update()


    @reactive.Effect
    @reactive.event(
        input.between_groups_night_and_day,
        # input.between_groups_swarmplot,
        # input.between_groups_stat_annotations,
        input.light_dark_selection,
        input.show_regression,
        input.ancova_full_model,
        input.use_welch,
        input.use_covariable,
        input.use_2wayfactor,
        input.between_groups_show_SEM,
        input.between_groups_show_feature,
    )
    def handleCheckboxChanges():
        between_groups_update()

    @output(id="between_groups_plot_measurement_1")
    @render_widget
    @reactive.event(between_groups_update_toggle)
    def between_groups_plot1_wrapper():
        return between_groups_plot_measurement_1()

    def between_groups_plot_measurement_1():
        try:
            if input.between_groups_measurement_no_1() not in caliData(session).getContinuousColumns():
                data = caliData(session).measurementFilteredGroupedDateTimeIndexed(
                    input.between_groups_measurement_no_1()
                )
                data_ungrouped = caliData(session).measurementFilteredDateTimeIndexed(
                    input.between_groups_measurement_no_1()
                )
                data_ungrouped = caliData(session).doGroupingByColumns(
                    data_ungrouped, caliData(session).groupedBy
                )
    
                spans = getAreasWhereDatetimIndexIs(
                    data,
                    lambda x: not caliData(session).night > x.time() > caliData(session).day,
                )
                fig = calorimetryDataPlot(
                    data,
                    data_ungrouped,
                    spans,
                    add_feature_peaks=input.between_groups_show_feature(),
                    feature_df=feature_func_var1(data_ungrouped),
                    add_sem=input.between_groups_show_SEM(),
                    xlabel_name=caliData(session).plotXlabelDay,
                )
                fig.update_layout(
                    yaxis_title=input.between_groups_measurement_no_1(),
                    xaxis_title="Time",
                    legend_title="",
                    height=450,
                )
                return fig
    
            elif input.between_groups_measurement_no_1() in caliData(session).getContinuousColumns():
                data = caliData(session).getContinuousColumnIndexedByBox(
                    input.between_groups_measurement_no_1()
                )
    
                fig = px.bar(data)
                fig.update_layout(
                    yaxis_title=input.between_groups_measurement_no_1(),
                    xaxis_title="Box",
                    legend_title="",
                    height=450,
                )
                return fig
        except Exception as e:
            print(f"Error in between_groups_plot_measurement_1: {e}")
            return create_empty_plot("")


    @output(id="between_groups_plot")
    @render_widget
    @reactive.event(between_groups_update_toggle)
    def between_groups_plot_wrapper():
        fig, stattext, data = between_groups_plot_and_stats()
        fig.update_layout(template="simple_white")
        return fig

    @reactive.event(between_groups_update_toggle)
    def between_groups_plot_and_stats():
        try:
            # ANOVA
            if not input.use_covariable():
                data = between_groups_data_anova()
                dependent_var = input.between_groups_measurement_no_1()
                # TODO: this is a dirty hack, think about fixing this to initial data load
                dependent_var = re.sub(r"\((\d+)\)", r"_\1", dependent_var)
                data.rename(columns={"value": dependent_var}, inplace=True)
    
                if input.between_groups_measurement_no_1() in caliData(session).getContinuousColumns():
                    if input.use_2wayfactor():
                        group_order = list(
                            return_conditional_continuous_variable(
                                input.between_groups_measurement_no_1()
                            )["group"]
                        )
                        fig = boxPlot_Betweengroups(
                            data,
                            dependent_var,
                            group_order,
                            "2wayanova",
                            scndfactor=input.between_groups_2way_factor(),
                        )
                        stat_result.set(
                            anova(
                                data,
                                dependent_var,
                                ["group", input.between_groups_2way_factor()]
                            )
                        )
                        stattext = (
                            "'2 Way ANOVA' function with '"
                            + input.between_groups_grouped()
                            + "' and '"
                            + input.between_groups_2way_factor()
                            + "' as predictive factors."
                        )
                    else:
                        group_order = list(
                            return_conditional_continuous_variable(
                                input.between_groups_measurement_no_1()
                            )["group"]
                        )

                        fig = boxPlot_Betweengroups(
                            data,
                            dependent_var,
                            group_order,
                            "anova",
                        )
                        stat_result.set(anova(data, dependent_var, "group", is_welch=input.use_welch()))
                        anovatext = "Welch " if input.use_welch() else ""
                        stattext = (
                            anovatext
                            + "'ANOVA' function with '"
                            + input.between_groups_grouped()
                            + "' as predictive factor."
                        )
                    return fig, stattext, data
                if input.between_groups_night_and_day():
                    group_order = list(
                        caliData(session)
                        .measurementFilteredGroupedDateTimeIndexed(
                            input.between_groups_measurement_no_1()
                        )
                        .columns
                    )[::-1]
                    fig = boxPlot_Betweengroups(data, dependent_var, group_order, "daynight")
                    stat_result.set(
                        anova(
                            data,
                            dependent_var,
                            ["group", "temp_condition"],
                            is_day_night=True,
                        )
                    )
                    stattext = (
                        "'ANOVA' function with '"
                        + input.between_groups_grouped()
                        + "' and 'temp_conditions'\nas predictive factors."
                        "'total' data were not taken into account for 2WAY ANOVA statistics."
                    )
                else:
                    group_order = list(
                        caliData(session)
                        .measurementFilteredGroupedDateTimeIndexed(
                            input.between_groups_measurement_no_1()
                        )
                        .columns
                    )[::-1]

                    if input.use_2wayfactor():
                        anovadata = two_way_anova_data(data)
                        stat_result.set(
                            anova(
                                anovadata,
                                dependent_var,
                                ["group", input.between_groups_2way_factor()],
                            )
                        )
                        fig = boxPlot_Betweengroups(
                            anovadata,
                            dependent_var,
                            group_order,
                            "2wayanova",
                            scndfactor=input.between_groups_2way_factor(),
                        )
                        stattext = (
                                "'2 Way ANOVA' function with '"
                                + input.between_groups_grouped()
                                + "' and '"
                                + input.between_groups_2way_factor()
                                + "' as predictive factors."
                        )
                    else:
                        fig = boxPlot_Betweengroups(data, dependent_var, group_order, "anova")
                        stat_result.set(anova(data, dependent_var, "group", is_welch=input.use_welch()))
                        anovatext = "Welch " if input.use_welch() else ""
                        stattext = (
                                anovatext
                                + "'ANOVA' function with '"
                                + input.between_groups_grouped()
                                + "' as predictive factor."
                        )
                    # Regressions
            else:
                if input.raw_feature() == RAW_DATA or input.raw_feature2() == RAW_DATA:
                    fig = show_error_message()
                    stat_result.set(None) # stat_result.set(pd.DataFrame())
                    data = pd.DataFrame()
                    stattext = "Statistics not possible, Regressions on raw data can be done using 'Between Variable Tab'"
                    return fig, stattext, data
                data = between_groups_data_regression()
    
                dependent_var = "value_y"
                dependent_var_name = input.between_groups_measurement_no_1()
                predicitve_var = "value_x"
                predictive_var_name = input.between_groups_measurement_no_2()
                data = data.rename(columns={"value_x": predictive_var_name})
    
                if input.between_groups_grouped() != "box":
                    data = data.rename(columns={"group_x": input.between_groups_grouped()})
                    if input.ancova_full_model():
                        full_model_result_table = calopy_ancova_full_model(data, dependent_var, predictive_var_name,
                                                                           input.between_groups_grouped())
                        stat_result.set(full_model_result_table)
                        stattext = (
                                " 'OLS regression' function with '"
                                + input.between_groups_grouped()
                                + "' and \n'"
                                + predictive_var_name
                                + "' as predictive variables including an interaction term."
                        )
                    else:
                        ancova_result_tbl = calopy_ancova(data, dependent_var, predictive_var_name, input.between_groups_grouped())
                        ancova_result_tbl["Source"] = ancova_result_tbl["Source"].replace(
                            {
                                "value_y": predictive_var_name,
                                "group_x": input.between_groups_grouped(),
                            }
                        )
                        stat_result.set(ancova_result_tbl)
                        stattext = (
                                "'ANCOVA' function with '"
                                + input.between_groups_grouped()
                                + "' as between factor and \n'"
                                + predictive_var_name
                                + "' as covariate."
                        )
                    fig = between_groups_regression_plot(data,
                                                         predictive_var_name,
                                                         predicitve_var,
                                                         dependent_var_name,
                                                         dependent_var,
                                                         input.between_groups_grouped()
                                                         )


                else:
                    ancova_result_tbl = calopy_regression(data[predictive_var_name], data[dependent_var])
                    ancova_result_tbl["names"] = ancova_result_tbl["names"].replace(
                        {
                            "value_y": predictive_var_name,
                            "group_x": input.between_groups_grouped(),
                        }
                    )
                    stat_result.set(ancova_result_tbl)
                    stattext = (
                        "'linear_regression' function with '"
                        + predicitve_var
                        + "' as predictive factor."
                    )
                    fig = between_groups_regression_plot(data,
                                                         predictive_var_name,
                                                         predicitve_var,
                                                         dependent_var_name,
                                                         dependent_var
                                                         )
    
            return fig, stattext, data
        
        except Exception as e:
            print(f"Error in between_groups_plot_and_stats: {e}")
            return create_empty_plot(""), "", ""

    @output(id="regression_residual_plot")
    @render_widget
    @reactive.event(between_groups_update_toggle)
    def plot_regression_residuals():
        try:
            res = stat_result().residuals_
            res = pd.DataFrame(res, columns=["Residuals"])
            fig = px.histogram(res, x="Residuals")
            fig.update_layout(template="simple_white", bargap=0.1)
            return fig
        except Exception as e:
            print(f"Error in plot_regression_residuals: {e}")
            return create_empty_plot("")


    def show_error_message():
        fig = go.Figure()
        fig.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[
                {
                    "text": "do not use RAW DATA for Regressions",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 20},
                }
            ],
        )
        return fig

    @output
    @render.table
    @reactive.event(between_groups_update_toggle)
    def between_groups_stat_result():
        # fig, stat_result, stattext, data = between_groups_plot_and_stats()
        return stat_result()

    @reactive.event(between_groups_update_toggle)
    def between_groups_data_anova():
        if input.between_groups_measurement_no_1() in caliData(session).getContinuousColumns():
            print("ANOVA on Conditional continuous variables")
            data = return_conditional_continuous_variable(input.between_groups_measurement_no_1())

        elif (
            input.raw_feature() == RAW_DATA
            and input.between_groups_measurement_no_1()
            not in caliData(session).getContinuousColumns()
        ):
            print("ANOVA on RAW DATA")
            data = caliData(session).measurementAndFiltered(
                input.between_groups_measurement_no_1()
            )
            if input.between_groups_night_and_day():
                data = NightAndDayFilter(caliData(session).night, caliData(session).day).apply(
                    data
                )
                data = between_groups_data_feature_filter_wrapper(data, feature_func_var1)
            else:
                data = between_groups_data_feature_filter_wrapper(data, feature_func_var1)
        else:
            print("ANOVA on extracted features")
            # day night filter
            if input.between_groups_night_and_day():
                data = caliData(session).measurementAndFiltered(
                    input.between_groups_measurement_no_1()
                )
                data = NightAndDayFilter(caliData(session).night, caliData(session).day).apply(
                    data
                )
                data = between_groups_data_feature_filter_wrapper(data, feature_func_var1)
            else:
                data = caliData(session).measurementAndFiltered(
                    input.between_groups_measurement_no_1()
                )
                data = between_groups_data_feature_filter_wrapper(data, feature_func_var1)
        return data

    def between_groups_data_feature_filter_wrapper(data, filter_func):
        if input.between_groups_night_and_day():
            feature_df_total = filter_func(data.xs("total", axis=1, level=0))
            feature_df_total["temp_condition"] = "total"
            feature_df_night = filter_func(data.xs("dark", axis=1, level=0))
            feature_df_night["temp_condition"] = "dark"
            feature_df_day = filter_func(data.xs("light", axis=1, level=0))
            feature_df_day["temp_condition"] = "light"
            data = pd.concat([feature_df_total, feature_df_night, feature_df_day])
            return data

        if input.light_dark_selection() == "total":
            data = filter_func(data)
        elif input.light_dark_selection() == "light":
            print("process light")
            data = NightAndDayFilter(caliData(session).night, caliData(session).day).apply(
                data
            )
            data = filter_func(data.xs("light", axis=1, level=0))
            data["temp_condition"] = "light"
        elif input.light_dark_selection() == "dark":
            data = NightAndDayFilter(caliData(session).night, caliData(session).day).apply(
                data
            )
            data = filter_func(data.xs("dark", axis=1, level=0))
            data["temp_condition"] = "dark"
        return data


    def between_groups_data_regression():
        print("Do Regression + ANCOVA")
        # get response data
        if input.between_groups_measurement_no_1() in caliData(session).getContinuousColumns():
            response_data = return_conditional_continuous_variable(
                input.between_groups_measurement_no_1()
            )
            response_data["feature"] = input.between_groups_measurement_no_1()
        else:
            data = caliData(session).measurementAndFiltered(
                input.between_groups_measurement_no_1()
            )
            response_data = between_groups_data_feature_filter_wrapper(data, feature_func_var1)
        # get coVar
        if input.between_groups_measurement_no_2() in caliData(session).getContinuousColumns():
            co_variable = return_conditional_continuous_variable(
                input.between_groups_measurement_no_2()
            )
            co_variable["feature"] = input.between_groups_measurement_no_2()
        else:
            data = caliData(session).measurementAndFiltered(
                input.between_groups_measurement_no_2()
            )
            co_variable = between_groups_data_feature_filter_wrapper(data, feature_func_var2)

        data = pd.merge(co_variable, response_data, left_on="box", right_on="box", how="left")
        return data

    def return_conditional_continuous_variable(input_var):
        print("return_conditional_continuous_variable")
        data = caliData(session).getContinuousColumnIndexedByBox(input_var)
        data = caliData(session).doGroupingByIndex(data, input.between_groups_grouped())
        data.index.name = "box"
        data = data.stack().reset_index()
        data.columns = ["box", "group", "value"]
        if input.use_2wayfactor():
            catdata = caliData(session).additionalData[["box", input.between_groups_2way_factor()]]
            data = pd.merge(data, catdata, on=["box"])
        return data

    def two_way_anova_data(indata):
        if input.raw_feature() == RAW_DATA:
            anovadata = caliData(session).doGroupingTwoFactors(
                caliData(session).measurementDateTimeIndexed(
                    input.between_groups_measurement_no_1()
                ),
                input.between_groups_grouped(),
                input.between_groups_2way_factor(),
            )
            # TODO: this is a dirty hack, think about moving this to initial data load
            pvar = re.sub(r"\((\d+)\)", r"_\1", input.between_groups_measurement_no_1())
            anovadata.rename(
                columns={input.between_groups_grouped(): "group", "value": pvar},
                inplace=True,
            )
            return anovadata
        else:
            catdata = caliData(session).additionalData[["box", input.between_groups_2way_factor()]]
            catdata = catdata.loc[:, ~catdata.columns.duplicated()].copy()
            anovadata = pd.merge(indata, catdata, on=["box"], how="left")
            return anovadata

    @output
    @render.plot
    @reactive.event(between_groups_update_toggle)
    def between_groups_Paired_plot_1():
        if (
            input.use_covariable()
            and input.between_groups_measurement_no_1()
            not in caliData(session).getContinuousColumns()
        ):
            fig, ax = plt.subplots()
            data_1 = caliData(session).measurementFilteredGroupedDateTimeIndexed(
                input.between_groups_measurement_no_1()
            )
            ax.set_ylabel(f"Measurement: {input.between_groups_measurement_no_1()}")
            data_1.plot(ax=ax)
            return fig

    @output
    @render.plot
    @reactive.event(between_groups_update_toggle)
    def between_groups_Paired_plot_2():
        if (
            input.use_covariable()
            and input.between_groups_measurement_no_2()
            not in caliData(session).getContinuousColumns()
        ):
            fig, ax = plt.subplots()
            data_1 = caliData(session).measurementFilteredGroupedDateTimeIndexed(
                input.between_groups_measurement_no_2()
            )
            ax.set_ylabel(f"Measurement: {input.between_groups_measurement_no_2()}")
            data_1.plot(ax=ax)
            return fig

    @output
    @render.download(
        filename=lambda: f"betweengroups_data_plot-{datetime.datetime.now().isoformat('_','seconds')}.pdf"
    )
    def betweengroups_plot1_downloader():
        fig = between_groups_plot_measurement_1()
        if fig is None:
            return "", "application/pdf"
        try:
            imb = fig.to_image(format="pdf", width=750, height=350, scale=1)
            buf = io.BytesIO(imb)
            buf.seek(0)
            return buf.getvalue(), "application/pdf"
        except:
            pass

    @output
    @render.download(
        filename=lambda: f"betweengroups_statistics_plot-{datetime.datetime.now().isoformat('_','seconds')}.pdf"
    )
    def betweengroups_plot2_downloader():
        fig, stattext, data = between_groups_plot_and_stats()
        if fig is None:
            return "", "application/pdf"
        try:
            imb = fig.to_image(format="pdf", width=450, height=350, scale=1)
            buf = io.BytesIO(imb)
            buf.seek(0)
            return buf.getvalue(), "application/pdf"
        except:
            pass

    @output
    @render.download(
        filename=lambda: f"between_groups_data-{datetime.datetime.now().isoformat('_','seconds')}.csv"
    )
    def betweengroups_data1_downloader():
        print("downloadData")
        if input.between_groups_measurement_no_1() in caliData(session).getContinuousColumns():
            data = caliData(session).getContinuousColumnIndexedByBox(
                input.between_groups_measurement_no_1()
            )
        else:
            data = caliData(session).measurementFilteredGroupedDateTimeIndexed(
                input.between_groups_measurement_no_1()
            )

        with io.BytesIO() as buf:
            data.to_csv(buf, sep=";", index=True)
            yield buf.getvalue()


    @output
    @render.download(
        filename=lambda: f"between_groups_data-{datetime.datetime.now().isoformat('_','seconds')}.csv"
    )
    def betweengroups_data2_downloader():
        print("downloadData")
        fig, stattext, data = between_groups_plot_and_stats()
        with io.BytesIO() as buf:
            data.to_csv(buf, sep=";", index=True)
            yield buf.getvalue()


    @render.download(
        filename=lambda: f"{input.between_groups_measurement_no_1()}-between_groups-stats-{datetime.datetime.now().isoformat()}.csv"
    )
    def betweengroups_stats_downloader():
        print("download stats")
        with io.BytesIO() as buf:
            stat_result().to_csv(buf, sep=",", index=True)
            yield buf.getvalue()

    @output
    @render.text
    def between_groups_stats_summary():
        fig, stattext, data = between_groups_plot_and_stats()
        reftext = ("[1] Vallat, R. (2018). Pingouin: statistics in Python. Journal of Open Source Software, 3(31), 1026,"
                   + "\nhttps://doi.org/10.21105/joss.01026"
                   + "\n[2] Seabold, S., & Perktold, J. (2010). statsmodels: Econometric and statistical modeling with python. In 9th Python in Science Conference."
                   + "\nhttps://www.statsmodels.org/"
                   )


        if input.ancova_full_model():
            textout = (
                    "Statistics was done using statsmodels[2] "
                    f"(v{statsmodels.__version__}) " + stattext + "\n\n" + reftext
            )
        else:
            textout = (
                "Statistics was done using Pingouin[1] "
                f"(v{pingouin.__version__}) " + stattext + "\n\n" + reftext
            )

        return textout
