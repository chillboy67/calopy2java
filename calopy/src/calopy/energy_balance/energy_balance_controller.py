import datetime
import io
import textwrap
import pandas as pd
import pingouin
from shiny import reactive, render, ui
from shinywidgets import render_widget
from plotly.subplots import make_subplots

from calopy.calopy_store import ENERGY_BALANCE_EE, ENERGY_BALANCE_EI, ENERGY_BALANCE_GROUPS, ENERGY_BALANCE_COVARIABLE,\
    caliData, caliState, calopyStore
from calopy.calopy_ui import ENERGYBALANCE

from calopy.maths.features import FEATURE_FUNC_DICT, TOTAL
from calopy.maths.statistic import anova, calopy_ancova
from calopy.maths.series_utils import getAreasWhereDatetimIndexIs, getIndexOf24HourInterval
from calopy.shared_ui.ICdataPlot import calorimetryDataPlot, conditionsStatsPlot
from calopy.shared_ui.boxplot import boxPlot_Betweengroups
from calopy.shared_ui.scatterplot import between_groups_regression_plot
from calopy.energy_balance.energy_balance_shiny import energy_balance_shiny

TO = "to"
FROM = "from"
TEXT = "Condition"
CONDITION = "condition"
FEATURE = "feature"
SAMPLE = "sample"
GROUP = "group"

ENERGY_EXPENDITURE = "energy_expenditure"
ENERGY_INTAKE = "energy_intake"
ENERGY_BALANCE = "energy_balance"




def energy_balance(input, output, session):
    energy_balance_update_toggle = reactive.Value(True)
    energy_balance_group = None
    featureFunc = FEATURE_FUNC_DICT[list(FEATURE_FUNC_DICT.keys())[1]]
    stat_result = reactive.Value(None)

    def energy_balance_update():
        print("energy_balance_update_ui")
        energy_balance_update_toggle.set(not energy_balance_update_toggle())

    @output
    @render.ui
    def energy_balance_ui():
        print("energy_balance_ui")
        return energy_balance_shiny

    @reactive.Effect
    @reactive.event(input.selected_feature)
    def energy_balanceSelectedFeature():
        print("selected_feature")
        if input.selected_feature() == ENERGYBALANCE:
            energy_balance_load_state()
            energy_balance_update()

    def energy_balance_load_state():
        print("preprocessed_load_state")
        energy_balance_update_toggle.set(not energy_balance_update_toggle())
        try:
            ui.update_select(
                "energy_expenditure_measurement",
                choices=caliData(session).measurements(),
                selected=caliState(session)[ENERGY_BALANCE_EE],
            )
            ui.update_select(
                "energy_intake_measurement",
                choices=caliData(session).measurements(),
                selected=caliState(session)[ENERGY_BALANCE_EI],
            )
            ui.update_select(
                "energy_balance_group",
                choices=caliData(session).getCategoricalColumns(),
                selected=caliState(session)[ENERGY_BALANCE_GROUPS],
            )
            ui.update_select(
                "energy_balance_covariable",
                choices=caliData(session).getContinuousColumns(),
                selected=caliState(session)[ENERGY_BALANCE_COVARIABLE],
            )
        except Exception as e:
            print("load_state failed")
            print(e)

    @reactive.Effect
    @reactive.event(input.energy_balance_group)
    def setGrouping():
        print("setGrouping")
        if caliData(session) is not None:
            caliData(session).setGrouping(input.energy_balance_group())
            caliState(session)[ENERGY_BALANCE_GROUPS] = input.energy_balance_group()
            energy_balance_update()

    @reactive.Effect
    @reactive.event(input.energy_balance_covariable)
    def setCovariable():
        print("setCovariable")
        if caliData(session) is not None:
            caliState(session)[ENERGY_BALANCE_COVARIABLE] = input.energy_balance_covariable()
            energy_balance_update()

    @reactive.Effect
    @reactive.event(input.energy_expenditure_measurement)
    def setMeasurementEE():
        print("setMeasurements")
        if caliState(session) is not None:
            caliState(session)[ENERGY_BALANCE_EE] = input.energy_expenditure_measurement()
            energy_balance_update()

    @reactive.Effect
    @reactive.event(input.energy_intake_measurement)
    def setMeasurementEI():
        print("setMeasurements")
        if caliState(session) is not None:
            caliState(session)[ENERGY_BALANCE_EI] = input.energy_intake_measurement()
            energy_balance_update()

    #@reactive.Effect
    #@reactive.event(energy_balance_update_toggle)
    def energy_balance_calculate():
        print("calculate energy balance")

        ei_data, ei_ungrouped = get_energy_intake_cumsum()
        ee_data, ee_ungrouped = get_energy_expenditure_cumsum()
        energy_balance_delta = ei_data - ee_data
        energy_balance_delta_ungrouped = ei_ungrouped - ee_ungrouped
        return energy_balance_delta, energy_balance_delta_ungrouped

    def get_energy_expenditure_cumsum():
        ee_data = caliData(session).measurementFilteredGroupedDateTimeIndexed(
            input.energy_expenditure_measurement()
        )

        ee_ungrouped = caliData(session).measurementFilteredDateTimeIndexed(
            input.energy_expenditure_measurement()
        )
        ee_ungrouped = caliData(session).doGroupingByColumns(
            ee_ungrouped, caliData(session).groupedBy
        )
        return ee_data.cumsum(), ee_ungrouped.cumsum()

    def get_energy_expenditure_totalsum():
        featureFunc = FEATURE_FUNC_DICT[TOTAL]
        ee_data =  caliData(session).measurementAndFiltered(
            input.energy_expenditure_measurement()
        )
        ee_total_sum = featureFunc(ee_data)
        return ee_total_sum

    def get_energy_intake_cumsum():
        ei_data = caliData(session).measurementFilteredGroupedDateTimeIndexed(
            input.energy_intake_measurement()
        )

        ei_ungrouped = caliData(session).measurementFilteredDateTimeIndexed(
            input.energy_intake_measurement()
        )
        ei_ungrouped = caliData(session).doGroupingByColumns(
            ei_ungrouped, caliData(session).groupedBy
        )
        return ei_data.cumsum(), ei_ungrouped.cumsum()

    def get_energy_intake_totalsum():
        featureFunc = FEATURE_FUNC_DICT[TOTAL]
        ei_data = caliData(session).measurementAndFiltered(
            input.energy_intake_measurement()
        )
        ei_total_sum = featureFunc(ei_data)
        return ei_total_sum

    @reactive.event(energy_balance_update_toggle)
    def energy_balance_total_sum_datatable():
        ee_totalsum = get_energy_expenditure_totalsum()
        ei_totalsum = get_energy_intake_totalsum()

        eb_table = pd.merge(ee_totalsum,
                            ei_totalsum,
                            on=["box", "group", "day_split", "feature"],
                            suffixes=("_ee", "_ei"))
        eb_table = eb_table.drop(columns=["index_ee", "index_ei"])
        eb_table["value_eb"] = eb_table["value_ei"] - eb_table["value_ee"]

        if input.energy_balance_group() != "box":
            group = caliData(session).additionalData[["box", input.energy_balance_group()]]
            eb_table = pd.merge(eb_table, group, on=["box"])

        covdata = caliData(session).additionalData[["box", input.energy_balance_covariable()]]
        eb_table = pd.merge(eb_table, covdata, on=["box"])

        return eb_table

    def energy_balance_statistics(eb_table, eb_value):
        if eb_value == "value_eb":
            return  anova(eb_table, eb_value, between="group")
        else:
             return  calopy_ancova(eb_table, eb_value, input.energy_balance_covariable(), between="group")

    @output(id="energy_balance_combined_plot")
    @render_widget
    @reactive.event(energy_balance_update_toggle, input.energy_balance_show_sem)
    def energy_balance_combined_plot_wrapper():
        return energy_balance_combined_plot()

    def energy_balance_combined_plot():

        fig_ei = energy_balance_plot_measurement_EI()
        fig_ee = energy_balance_plot_measurement_EE()
        fig_eb = energy_balance_plot_delta()

        combined_fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=[
                f"Energy Intake",
                f"Energy Expenditure",
                f"Energy Balance"
            ]
        )

        for trace in fig_ei.data:
            trace.showlegend = False
            if trace.name is None:
                trace.name = ""
            combined_fig.add_trace(trace, row=1, col=1)
        for trace in fig_ee.data:
            trace.showlegend = False
            if trace.name is None:
                trace.name = ""
            combined_fig.add_trace(trace, row=2, col=1)
        for trace in fig_eb.data:
            trace.showlegend = True
            if not trace.name:
                trace.name = "Energy Balance"  # or some default name
            combined_fig.add_trace(trace, row=3, col=1)

        # After adding traces to combined_fig
        for shape in fig_ei.layout.shapes:
            combined_fig.add_shape(shape, row=1, col=1)
        for shape in fig_ee.layout.shapes:
            combined_fig.add_shape(shape, row=2, col=1)
        for shape in fig_eb.layout.shapes:
            combined_fig.add_shape(shape, row=3, col=1)

        # Optionally update layout
        combined_fig.update_layout(
            height=700,
            showlegend=True,
            legend_title="",
        )
        combined_fig.update_xaxes(title_text="Time", row=3, col=1)
        combined_fig.update_yaxes(title_text=f"{input.energy_intake_measurement()} (cum sum)", row=1, col=1)
        combined_fig.update_yaxes(title_text=f"{input.energy_expenditure_measurement()} (cum sum)", row=2, col=1)
        combined_fig.update_yaxes(title_text="Energy Balance", row=3, col=1)

        combined_fig.update_layout(
            template="simple_white",
        ),

        return combined_fig

    def energy_balance_plot_measurement_EI():
        data, data_ungrouped = get_energy_intake_cumsum()
        data.columns = data.columns.get_level_values(-1)
        spans = getAreasWhereDatetimIndexIs(
            data,
            lambda x: not caliData(session).night > x.time() > caliData(session).day,
        )
        fig = calorimetryDataPlot(
            data,
            data_ungrouped,
            spans,
            add_feature_peaks=False,
            feature_df=None,
            add_sem=input.energy_balance_show_sem(),
            xlabel_name=caliData(session).plotXlabelDay,
        )
        fig.update_layout(
            yaxis_title=input.energy_intake_measurement(),
            xaxis_title="Time",
            legend_title="",
            height=350,
        )
        return fig

    def energy_balance_plot_measurement_EE():
        data, data_ungrouped = get_energy_expenditure_cumsum()
        data.columns = data.columns.get_level_values(-1)
        spans = getAreasWhereDatetimIndexIs(
            data,
            lambda x: not caliData(session).night > x.time() > caliData(session).day,
        )
        fig = calorimetryDataPlot(
            data,
            data_ungrouped,
            spans,
            add_feature_peaks=False,
            feature_df=None,
            add_sem=input.energy_balance_show_sem(),
            xlabel_name=caliData(session).plotXlabelDay,
        )
        fig.update_layout(
            yaxis_title=input.energy_expenditure_measurement(),
            xaxis_title="Time",
            legend_title="",
            height=350,
        )
        return fig

    def energy_balance_plot_delta():
        data, data_ungrouped = energy_balance_calculate()
        data.columns = data.columns.get_level_values(-1)
        spans = getAreasWhereDatetimIndexIs(
            data,
            lambda x: not caliData(session).night > x.time() > caliData(session).day,
        )
        fig = calorimetryDataPlot(
            data,
            data_ungrouped,
            spans,
            add_feature_peaks=False,
            feature_df=None,
            add_sem=input.energy_balance_show_sem(),
            xlabel_name=caliData(session).plotXlabelDay,
        )
        fig.update_layout(
            yaxis_title=input.energy_intake_measurement(),
            xaxis_title="Time",
            legend_title="",
            height=350,
        )
        return fig

    @output(id="energy_balance_stats_plot")
    @render_widget
    @reactive.event(energy_balance_update_toggle, input.energy_balance_show_sem)
    def energy_balance_stats_plot_wrapper():
        return energy_balance_stats_combined_plot()

    def energy_balance_stats_combined_plot():
        fig_ei = energy_balance_ancova_plot("value_ei")
        fig_ee = energy_balance_ancova_plot("value_ee")
        fig_eb = energy_balance_stats_plot("value_eb")

        combined_fig = make_subplots(
            rows=1, cols=3,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=[
                f"Energy Intake",
                f"Energy Expenditure",
                f"Energy Balance"
            ]
        )
        for trace in fig_ei.data:
            trace.showlegend = False
            combined_fig.add_trace(trace, row=1, col=1)
        for trace in fig_ee.data:
            trace.showlegend = False
            combined_fig.add_trace(trace, row=1, col=2)
        for trace in fig_eb.data:
            trace.showlegend = True
            combined_fig.add_trace(trace, row=1, col=3)

        combined_fig.update_xaxes(title_text=input.energy_balance_covariable(), row=1, col=1)
        combined_fig.update_xaxes(title_text=input.energy_balance_covariable(), row=1, col=2)
        combined_fig.update_xaxes(title_text="Group", row=1, col=3)
        combined_fig.update_yaxes(title_text=f"{input.energy_intake_measurement()} (sum)", row=1, col=1)
        combined_fig.update_yaxes(title_text=f"{input.energy_expenditure_measurement()} (sum)", row=1, col=2)
        combined_fig.update_yaxes(title_text="Energy Balance", row=1, col=3)
        combined_fig.update_layout(
            template="simple_white",
        ),

        return combined_fig

    def energy_balance_stats_plot(dep_var):
        plotdata = energy_balance_total_sum_datatable()
        group_order = list(caliData(session).measurementFilteredGroupedDateTimeIndexed(
                input.energy_intake_measurement()
            ).columns
        )[::-1]
        fig = boxPlot_Betweengroups(
                            plotdata,
                            dep_var,
                            group_order,
                            "anova",
                        )
        return fig

    def energy_balance_ancova_plot(dep_var):
        plotdata = energy_balance_total_sum_datatable()
        predictive_var_name = input.energy_balance_covariable()
        plotdata = plotdata.rename(columns={"value_x": predictive_var_name})
        plotdata["feature_x"] = predictive_var_name
        plotdata = plotdata.rename(columns={"feature": "feature_y"})
        plotdata = plotdata.rename(columns={"value_y": dep_var})

        fig = between_groups_regression_plot(plotdata,
                                             predictive_var_name,
                                             "value_x",
                                             dep_var,
                                             dep_var,
                                             input.energy_balance_group()
                                             )
        return fig


    @output
    @render.download(
        filename=lambda: f"energy_balance_plot-{datetime.datetime.now().isoformat('_', 'seconds')}.pdf"
    )
    def energy_balance_plot_downloader():
        fig = energy_balance_combined_plot()
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
        filename=lambda: f"energy_balance_data-{datetime.datetime.now().isoformat('_', 'seconds')}.csv"
    )
    def energy_balance_data_downloader():
        data_ei, data_ungrouped = get_energy_intake_cumsum()
        data_ee, data_ungrouped = get_energy_expenditure_cumsum()
        data_eb, data_ungrouped = energy_balance_calculate()

        header_ei = pd.DataFrame([["--- CUMULATIVE ENERGY INTAKE (kcal) ---"]], columns=[""])
        header_ee = pd.DataFrame([["--- CUMULATIVE ENERGY EXPENDITURE (kcal) ---"]], columns=[""])
        header_eb = pd.DataFrame([["--- ENERGY BALANCE (kcal) ---"]], columns=[""])

        data_ei_labeled = data_ei.copy().reset_index()
        data_ee_labeled = data_ee.copy().reset_index()
        data_eb_labeled = data_eb.copy().reset_index()

        data_ei_labeled = data_ei_labeled.astype(str)
        data_ee_labeled = data_ee_labeled.astype(str)
        data_eb_labeled = data_eb_labeled.astype(str)

        combined_data = pd.concat([
            header_ei, data_ei_labeled,
            header_ee, data_ee_labeled,
            header_eb, data_eb_labeled
        ], ignore_index=True)

        # Write combined CSV to buffer
        buf = io.BytesIO()
        buf.write(combined_data.to_csv(index=False).encode("utf-8"))
        buf.seek(0)
        return buf.getvalue(), "text/csv"

    @output
    @render.download(
        filename=lambda: f"energy_balance_boxplot-{datetime.datetime.now().isoformat('_', 'seconds')}.pdf"
    )
    def energy_balance_boxplot_downloader():
        fig = energy_balance_stats_combined_plot()
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
        filename=lambda: f"energy_balance_statistics_data-{datetime.datetime.now().isoformat('_', 'seconds')}.csv"
    )
    def energy_balance_boxplot_data_downloader():
        data = energy_balance_total_sum_datatable()

        # Write combined CSV to buffer
        buf = io.BytesIO()
        buf.write(data.to_csv(index=False).encode("utf-8"))
        buf.seek(0)
        return buf.getvalue(), "text/csv"

    @output
    @render.table
    @reactive.event(energy_balance_update_toggle)
    def energy_balance_stat_result_ei(short_table = True):
        data = energy_balance_total_sum_datatable()
        stats_ei = energy_balance_statistics(data, "value_ei")
        return stats_ei[["Source", "p-unc"]]

    @output
    @render.table
    @reactive.event(energy_balance_update_toggle)
    def energy_balance_stat_result_ee(short_table = True):
        data = energy_balance_total_sum_datatable()
        stats_ee = energy_balance_statistics(data, "value_ee")
        if short_table:
            return stats_ee[["Source", "p-unc"]]
        else:
            return stats_ee


    @output
    @render.table
    @reactive.event(energy_balance_update_toggle)
    def energy_balance_stat_result_eb(short_table = True):
        data = energy_balance_total_sum_datatable()
        stats_eb = energy_balance_statistics(data, "value_eb")
        return stats_eb[["Source", "p-unc"]]

    @output
    @render.text
    @reactive.event(energy_balance_update_toggle)
    def energy_balance_stats_summary():
        version = pingouin.__version__
        group = input.energy_balance_group()
        covar = input.energy_balance_covariable()

        reftext = (
            "[1] Vallat, R. (2018). Pingouin: statistics in Python. "
            "Journal of Open Source Software, 3(31), 1026.\n"
            "https://doi.org/10.21105/joss.01026"
        )

        textout = f"""\
Statistics on Energy Intake (EI) & Energy Expenditure (EE) were performed using
Pingouin [1] (v{version}) with the ANCOVA function, applied to the total sums of
EI and EE, using '{group}' as the between-subject factor and '{covar}' as the covariate.

Statistics on Energy Balance (EB = EI – EE) were performed using
Pingouin [1] (v{version}) with the ANOVA function, using '{group}' as the grouping factor.

{reftext}
"""
        return textwrap.dedent(textout).strip()


    @output
    @render.download(
        filename=lambda: f"energy_balance_stats-{datetime.datetime.now().isoformat()}.csv"
    )
    def energy_balance_stats_downloader():
        data = energy_balance_total_sum_datatable()
        stats_ei = energy_balance_statistics(data, "value_ei")
        stats_ee = energy_balance_statistics(data, "value_ee")
        stats_eb = energy_balance_statistics(data, "value_eb")

        header_ei = pd.DataFrame([["--- ANOVA TABLE ENERGY INTAKE ---"]], columns=[""])
        header_ee = pd.DataFrame([["--- ANOVA TABLE ENERGY EXPENDITURE ---"]], columns=[""])
        header_eb = pd.DataFrame([["--- ANOVA TABLE ENERGY BALANCE ---"]], columns=[""])

        data_ei_labeled = stats_ei.copy().reset_index()
        data_ee_labeled = stats_ee.copy().reset_index()
        data_eb_labeled = stats_eb.copy().reset_index()

        data_ei_labeled = data_ei_labeled.astype(str)
        data_ee_labeled = data_ee_labeled.astype(str)
        data_eb_labeled = data_eb_labeled.astype(str)

        combined_data = pd.concat([
            header_ei, data_ei_labeled,
            header_ee, data_ee_labeled,
            header_eb, data_eb_labeled
        ], ignore_index=True)

        # Write combined CSV to buffer
        buf = io.BytesIO()
        buf.write(combined_data.to_csv(index=False).encode("utf-8"))
        buf.seek(0)
        return buf.getvalue(), "text/csv"