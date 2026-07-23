import datetime
import io

import pandas as pd
import plotly.express as px
import plotly.io as pio
from pypdf import PdfWriter
from shiny import reactive, render, ui
from shinywidgets import render_widget
from tabulate import tabulate

from calopy.calopy_store import caliData, calopyStore
from calopy.calopy_ui import PREPROCESSING, SMOOTHING
from calopy.maths.filter.DoNothingOnSeriesFilter import DO_NOTHING, DoNothingOnSeriesFilter
from calopy.maths.filter.GeneralizedAdditiveFilter import GENERALIZED_ADDITIVE, \
                                                          GeneralizedAdditiveFilter
from calopy.maths.filter.RollingWindowGausianFilter import ROLLING_WINDOW_GAUSIAN, \
                                                           RollingWindowGausianFilter
from calopy.maths.filter.RollingWindowMeanFilter import ROLLING_WINDOW, RollingWindowMeanFilter
from calopy.maths.filter.RollingWindowTriangularFilter import ROLLING_WINDOW_TRIANGULAR, \
                                                              RollingWindowTriangularFilter
from calopy.maths.filter.SavgolFilter import SAVGOL, SavgolFilter
from calopy.maths.filter.SingleComponentCosinorFilter import SINGLE_COMPONENT_COSINOR, \
                                                             SingleComponentCosinorFilter
from calopy.maths.filter.UnivariateSplineAutofitFilter import UNVAR_SPLINE_AUTOFIT, \
                                                              UnivarateSplineAutofitFilter
from calopy.maths.filter.UnivariateSplineFilter import UNVAR_SPLINE, UnivariateSpline
from calopy.maths.series_utils import getAreasWhereDatetimIndexIs, getIndexOf24HourInterval
from calopy.shared_ui.plot_config import COLOR_DATECHANGE, COLOR_NIGHTTIME, create_empty_plot
from calopy.smoothing.smoothing_shiny import smoothing_shiny

# pio.kaleido.scope.mathjax = None  ### avoids mathjax message for first pdf export https://github.com/plotly/plotly.py/issues/3469


def smoothing(input, output, session):
    smoothing_update_toggle = reactive.Value(True)
    smoothing_measurement = None
    smoothing_sampleToShow = reactive.Value(0)

    def smoothing_update():
        print("smoothing_update_ui")
        smoothing_update_toggle.set(not smoothing_update_toggle())

    @output
    @render.ui
    def smoothing_ui():
        print("smoothing_ui")
        return smoothing_shiny

    @reactive.Effect
    @reactive.event(input.selected_feature)
    def smoothing_selected_feature():
        print("smoothing_selected_feature")
        if input.selected_feature() == SMOOTHING:
            smoothing_load_state()
            smoothing_update()

    def smoothing_load_state():
        try:
            ui.update_select(
                "smoothing_current_measurement",
                choices=caliData(session).measurements(),
                selected=smoothing_measurement,
            )
        except Exception as e:
            print("smoothing_load_state failed")
            print(e)

    @output(id="smoothing_plot")
    @render_widget
    @reactive.event(smoothing_update_toggle)
    def smoothing_plot_wrapper():
        ### necessary for download fig
        return smoothing_plot()

    def smoothing_plot(sampleId=None):
        print("smoothing_plot")
        try:
            data_raw_all = caliData(session).measurementDateTimeIndexed(
                input.smoothing_current_measurement()
            )
            data_raw = filtering(
                caliData(session).measurementDateTimeIndexed(input.smoothing_current_measurement()),
                sampleId=sampleId,
            )
            data_smooth = filtering(
                caliData(session).measurementFilteredDateTimeIndexed(
                    input.smoothing_current_measurement()
                ),
                sampleId=sampleId,
            )
            data_plot = pd.concat([data_raw, data_smooth], axis=1)
            data_plot.columns = [
                data_plot.columns[0] + "_raw",
                data_plot.columns[0] + "_smooth",
            ]
    
            spans = getAreasWhereDatetimIndexIs(
                data_plot,
                lambda x: not caliData(session).night > x.time() > caliData(session).day,
            )
    
            ### make all files start on 1st january to show day 1 instead of exact date in plot
            if caliData(session).plotXlabelDay == "day":
                days_difference = (
                    pd.Timestamp("2018-01-01").date() - data_raw_all.index[0].date()
                ).days -1
                data_raw_all.index = data_raw_all.index + pd.DateOffset(days=days_difference)
                data_plot.index = data_plot.index + pd.DateOffset(days=days_difference)
                spans = [
                    (
                        start + pd.DateOffset(days=days_difference),
                        end + pd.DateOffset(days=days_difference),
                    )
                    for start, end in spans
                ]
    
            y_limit_range = [min(data_raw_all.min()), max(data_raw_all.max())]
            fig = px.line(data_plot, color_discrete_sequence=["#ffb3b3", "#E10000"])
    
            for x, y in spans:
                fig.add_vrect(
                    x0=x,
                    x1=y,
                    fillcolor=COLOR_NIGHTTIME,
                    line_width=0,
                    layer="below",
                    opacity=1,
                )
    
            for daychange in getIndexOf24HourInterval(data_plot.index):
                fig.add_vline(
                    x=daychange,
                    line_width=2,
                    line_dash="dash",
                    line_color=COLOR_DATECHANGE,
                    opacity=1,
                    layer="below",
                )
    
            fig.update_yaxes(range=y_limit_range)
            fig.update_layout(
                yaxis_title=input.smoothing_current_measurement(),
                xaxis_title="Time",
                legend_title="",
                template="simple_white",
                height=450,
            )
            fig.update_xaxes(showline=True, linewidth=1, linecolor="black", ticks="outside")
            fig.update_yaxes(showline=True, linewidth=1, linecolor="black", ticks="outside")
    
            if caliData(session).plotXlabelDay == "day":
                fig.update_xaxes(tickformat="%H:%M\nDay %_j")  ### show day 1 instead of exact date
    
            return fig
        except Exception as e:
            print(f"Error in smoothing_plot: {e}")
            return create_empty_plot("")

    @reactive.Effect
    @reactive.event(input.smoothing_current_measurement)
    def currentMeasurement():
        print("setCurrentMeasurement")
        nonlocal smoothing_measurement
        smoothing_measurement = input.smoothing_current_measurement()
        type = caliData(session).filter.getSmoothing(smoothing_measurement).type
        ui.update_select("smoothing_curve_fitting_method", selected=type)
        if type == ROLLING_WINDOW:
            ui.update_numeric(
                "smoothing_curve_fitting_param_1",
                value=caliData(session).filter.getSmoothing(smoothing_measurement).window,
            )
        if type == UNVAR_SPLINE:
            ui.update_numeric(
                "smoothing_curve_fitting_param_1",
                value=caliData(session).filter.getSmoothing(smoothing_measurement).smoothingfactor,
            )
        if type == ROLLING_WINDOW_TRIANGULAR:
            ui.update_numeric(
                "smoothing_curve_fitting_param_1",
                value=caliData(session).filter.getSmoothing(smoothing_measurement).window,
            )
        if type == ROLLING_WINDOW_GAUSIAN:
            ui.update_numeric(
                "smoothing_curve_fitting_param_1",
                value=caliData(session).filter.getSmoothing(smoothing_measurement).window,
            )
            ui.update_numeric(
                "smoothing_curve_fitting_param_2",
                value=caliData(session).filter.getSmoothing(smoothing_measurement).deviation,
            )
        if type == SAVGOL:
            ui.update_numeric(
                "smoothing_curve_fitting_param_1",
                value=caliData(session).filter.getSmoothing(smoothing_measurement).window,
            )
            ui.update_numeric(
                "smoothing_curve_fitting_param_2",
                value=caliData(session).filter.getSmoothing(smoothing_measurement).order,
            )

        oulierFilter = caliData(session).filter.getOutlier(smoothing_measurement)
        if oulierFilter.type == DO_NOTHING:
            ui.update_checkbox("smoothing_outlier_remove", value=False)
        else:
            ui.update_checkbox("smoothing_outlier_remove", value=True)
            ui.update_numeric("smoothing_outlier_threshold", value=oulierFilter.outlierVal)
        smoothing_update()

    @reactive.Effect
    @reactive.event(input.smoothing_outlier_threshold, input.smoothing_outlier_remove)
    def removeOutliers():
        print("removeOutliers")
        try:
            caliData(session).filter.applyOutlierFunc(
                input.smoothing_current_measurement(),
                input.smoothing_outlier_remove(),
                input.smoothing_outlier_threshold(),
            )
            smoothing_update()
        except Exception as e:
            print("Error removing outliers: " + str(e))

    @reactive.Effect
    @reactive.event(
        input.smoothing_curve_fitting_method,
        input.smoothing_curve_fitting_param_1,
        input.smoothing_curve_fitting_param_2,
    )
    def curveFitting():
        print("curveFitting")
        try:
            curveFittingMeasurement(
                input.smoothing_current_measurement(),
                input.smoothing_curve_fitting_method(),
            )
            smoothing_update()
        except Exception as e:
            print("Error curve fitting: " + str(e))

    def curveFittingMeasurement(currMeasurement, currMethod):
        print("curveFittingMeasurement")
        try:
            # type = input.smoothing_curve_fitting_method()
            type = currMethod
            print("type: " + str(type))

            max_window_size = (
                caliData(session).measurementDateTimeIndexed(currMeasurement).shape[0] - 2
            )

            if type == DO_NOTHING:
                caliData(session).filter.setSmoothing(currMeasurement, DoNothingOnSeriesFilter())
            if type == GENERALIZED_ADDITIVE:
                caliData(session).filter.setSmoothing(currMeasurement, GeneralizedAdditiveFilter())
            if type == ROLLING_WINDOW:
                ui.update_numeric(
                    "smoothing_curve_fitting_param_1",
                    min=2,
                    step=1,
                    max=max_window_size,
                    label="window size",
                )
                caliData(session).filter.setSmoothing(
                    currMeasurement,
                    RollingWindowMeanFilter(input.smoothing_curve_fitting_param_1()),
                )
            if type == UNVAR_SPLINE:
                ui.update_numeric(
                    "smoothing_curve_fitting_param_1",
                    min=0.01,
                    step=0.01,
                    max=100,
                    label="smoothing factor",
                )
                caliData(session).filter.setSmoothing(
                    currMeasurement,
                    UnivariateSpline(input.smoothing_curve_fitting_param_1()),
                )
            if type == ROLLING_WINDOW_TRIANGULAR:
                ui.update_numeric(
                    "smoothing_curve_fitting_param_1",
                    min=2,
                    step=1,
                    max=max_window_size,
                    label="window size",
                )
                caliData(session).filter.setSmoothing(
                    currMeasurement,
                    RollingWindowTriangularFilter(input.smoothing_curve_fitting_param_1()),
                )
            if type == ROLLING_WINDOW_GAUSIAN:
                ui.update_numeric(
                    "smoothing_curve_fitting_param_1",
                    min=2,
                    step=1,
                    max=max_window_size,
                    label="window size",
                )
                ui.update_numeric(
                    "smoothing_curve_fitting_param_2",
                    min=1,
                    step=1,
                    max=20,
                    label="standard deviation",
                )
                caliData(session).filter.setSmoothing(
                    currMeasurement,
                    RollingWindowGausianFilter(
                        input.smoothing_curve_fitting_param_1(),
                        input.smoothing_curve_fitting_param_2(),
                    ),
                )
            if type == UNVAR_SPLINE_AUTOFIT:
                caliData(session).filter.setSmoothing(
                    currMeasurement, UnivarateSplineAutofitFilter()
                )
            if type == SAVGOL:
                ui.update_numeric(
                    "smoothing_curve_fitting_param_1",
                    min=2,
                    step=1,
                    max=max_window_size,
                    label="window size",
                )
                ui.update_numeric(
                    "smoothing_curve_fitting_param_2",
                    min=0,
                    max=input.smoothing_curve_fitting_param_1() - 1,
                    value=max(
                        min(
                            input.smoothing_curve_fitting_param_2(),
                            (input.smoothing_curve_fitting_param_1() - 1),
                        ),
                        0,
                    ),
                    step=1,
                    label="polynom order",
                )
                caliData(session).filter.setSmoothing(
                    currMeasurement,
                    SavgolFilter(
                        input.smoothing_curve_fitting_param_1(),
                        input.smoothing_curve_fitting_param_2(),
                    ),
                )
            if type == SINGLE_COMPONENT_COSINOR:
                caliData(session).filter.setSmoothing(
                    currMeasurement,
                    SingleComponentCosinorFilter(caliData(session).timestepsPerDay()),
                )

        except Exception as e:
            print("Error curve fitting: " + str(e))

    @output
    @render.text
    @reactive.event(smoothing_update_toggle)
    def smoothing_parameter_info():
        if caliData(session) is not None:
            print("smoothing_parameter_info")
            smoothing_dict_output = dict(
                (k, [v.type, v.get_parameter_text()])
                for k, v in caliData(session).filter.smoothing.items()
            )
            outlier_dict_output = dict(
                (k, [v.type, v.get_parameter_text()])
                for k, v in caliData(session).filter.outlier.items()
            )
            output_df = pd.concat(
                [
                    pd.DataFrame(smoothing_dict_output).T,
                    pd.DataFrame(outlier_dict_output).T,
                ],
                axis=1,
            )
            output_df.columns = [
                "smoothing_function",
                "smoothing_parameter",
                "outlier_removal",
                "outlier_parameter",
            ]
            output_df = output_df.replace("Do nothing", "")
            return tabulate(output_df, output_df.columns, tablefmt="simple")
        else:
            return None

    @reactive.Effect
    @reactive.event(input.smoothing_fit_apply_on_all)
    def smoothing_fit_apply_on_all():
        if caliData(session) is not None:
            print("smoothing_fit_apply_on_all")
            for curr_meas in caliData(session).measurements():
                curveFittingMeasurement(curr_meas, input.smoothing_curve_fitting_method())
            smoothing_update()

    @reactive.Effect
    @reactive.event(input.smoothing_fit_reset)
    def smoothing_fit_reset():
        if caliData(session) is not None:
            print("smoothing_fit_reset")
            for curr_meas in caliData(session).measurements():
                curveFittingMeasurement(curr_meas, DO_NOTHING)
            smoothing_update()

    @reactive.Effect
    @reactive.event(input.smoothing_outlier_apply_on_all)
    def smoothing_outlier_apply_on_all():
        if caliData(session) is not None:
            print("smoothing_outlier_apply_on_all")
            for curr_meas in caliData(session).measurements():
                caliData(session).filter.applyOutlierFunc(
                    curr_meas,
                    input.smoothing_outlier_remove(),
                    input.smoothing_outlier_threshold(),
                )
            smoothing_update()

    @reactive.Effect
    @reactive.event(input.smoothing_outlier_reset)
    def smoothing_outlier_reset():
        if caliData(session) is not None:
            print("smoothing_outlier_reset")
            for curr_meas in caliData(session).measurements():
                caliData(session).filter.applyOutlierFunc(
                    curr_meas, False, input.smoothing_outlier_threshold()
                )
            smoothing_update()

    @reactive.Effect
    @reactive.event(input.removeOutliers_apply_on_all)
    def removeOutliers_apply_on_all():
        if caliData(session) is not None:
            print("removeOutliers_apply_on_all")
            for curr_meas in caliData(session).measurements():
                caliData(session).filter.applyOutlierFunc(
                    curr_meas, True, input.smoothing_outlier_threshold()
                )
            smoothing_update()

    @reactive.Effect
    @reactive.event(input.smoothing_plot_prev)
    def smoothing_plot_prev():
        if caliData(session) is not None:
            index = smoothing_sampleToShow()
            index -= 1
            if index < 0:
                index = (
                    caliData(session)
                    .measurementDateTimeIndexed(input.smoothing_current_measurement())
                    .columns.size
                    - 1
                )
            smoothing_sampleToShow.set(index)
            smoothing_update()

    @reactive.Effect
    @reactive.event(input.smoothing_plot_next)
    def smoothing_plot_next():
        if caliData(session) is not None:
            index = smoothing_sampleToShow()
            index += 1
            if (
                index
                >= caliData(session)
                .measurementDateTimeIndexed(input.smoothing_current_measurement())
                .columns.size
            ):
                index = 0
            smoothing_sampleToShow.set(index)
            smoothing_update()

    def filtering(data: pd.DataFrame, sampleId=None):
        if sampleId is None:
            return data.get(data.columns.tolist()[smoothing_sampleToShow()])
        else:
            return data.get(sampleId)

    @output
    @render.text
    def smoothing_plot_sample():
        try: 
            curr_sample = caliData(session).measurementDateTimeIndexed(input.smoothing_current_measurement()).columns.tolist()[smoothing_sampleToShow()]
        except:
            curr_sample = ""
        return curr_sample

    @render.download(
        filename=lambda: f"{input.smoothing_current_measurement()}-smoothed-download-{datetime.datetime.now().isoformat('_','seconds')}.csv"
    )
    def smoothed_data_downloader():
        print("downloadData")
        data = caliData(session).measurementFilteredDateTimeIndexed(
            input.smoothing_current_measurement()
        )
        with io.BytesIO() as buf:
            data.to_csv(buf, sep=";", index=True)
            yield buf.getvalue()

    @render.download(
        filename=lambda: f"{input.smoothing_current_measurement()}-smoothed-plot-{datetime.datetime.now().isoformat('_','seconds')}.pdf"
    )
    def smoothed_plot_downloader():
        pdf_writer = PdfWriter()
        with io.BytesIO() as buf:
            for sample_id in caliData(session).samplesWithoutExcluded():
                # buf_tmp = io.BytesIO()
                # fig = smoothing_plot(sampleId=sample_id)
                # pio.write_image(fig, buf_tmp, 'pdf')
                #
                # buf_tmp.seek(0)
                # pdf_writer.append(buf_tmp)

                fig = smoothing_plot(sampleId=sample_id)
                imb = fig.to_image(format="pdf", width=750, height=350, scale=1)
                buf_tmp = io.BytesIO(imb)
                buf_tmp.seek(0)
                pdf_writer.append(buf_tmp)

            pdf_writer.write(buf)
            yield buf.getvalue()
