from shiny import ui
from shinywidgets import output_widget

from calopy.maths.filter.DoNothingOnSeriesFilter import DO_NOTHING
from calopy.maths.filter.GeneralizedAdditiveFilter import GENERALIZED_ADDITIVE
from calopy.maths.filter.RollingWindowGausianFilter import ROLLING_WINDOW_GAUSIAN
from calopy.maths.filter.RollingWindowMeanFilter import ROLLING_WINDOW
from calopy.maths.filter.RollingWindowTriangularFilter import ROLLING_WINDOW_TRIANGULAR
from calopy.maths.filter.SavgolFilter import SAVGOL
from calopy.maths.filter.SingleComponentCosinorFilter import SINGLE_COMPONENT_COSINOR
from calopy.maths.filter.UnivariateSplineAutofitFilter import UNVAR_SPLINE_AUTOFIT
from calopy.maths.filter.UnivariateSplineFilter import UNVAR_SPLINE

smooth_method_list = [
    DO_NOTHING,
    GENERALIZED_ADDITIVE,
    ROLLING_WINDOW,
    ROLLING_WINDOW_TRIANGULAR,
    ROLLING_WINDOW_GAUSIAN,
    UNVAR_SPLINE,
    UNVAR_SPLINE_AUTOFIT,
    SAVGOL,
    SINGLE_COMPONENT_COSINOR,
]

smoothing_shiny = ui.layout_sidebar(
    ui.sidebar(
        ui.h5("Variable Selection"),
        ui.input_select("smoothing_current_measurement", "Select metabolic variable", []),
        # ui.input_select("smoothing_grouped", "grouping", []),
        ui.hr(style="margin: 4px 0;"),
        ui.h5("Curve Fitting"),
        ui.input_select("smoothing_curve_fitting_method", "Select method", smooth_method_list),
        ui.panel_conditional(
            "['"
            + SAVGOL
            + "','"
            + UNVAR_SPLINE
            + "','"
            + ROLLING_WINDOW_TRIANGULAR
            + "','"
            + ROLLING_WINDOW
            + "','"
            + ROLLING_WINDOW_GAUSIAN
            + "'].includes(input.smoothing_curve_fitting_method)",
            ui.input_numeric(
                "smoothing_curve_fitting_param_1",
                "parameter",
                value=1,
                min=1,
                max=10,
                step=1,
            ),
        ),
        ui.panel_conditional(
            "['"
            + SAVGOL
            + "','"
            + ROLLING_WINDOW_GAUSIAN
            + "'].includes(input.smoothing_curve_fitting_method)",
            ui.input_numeric(
                "smoothing_curve_fitting_param_2",
                "parameter",
                value=2,
                min=1,
                max=10,
                step=1,
            ),
        ),
        ui.row(
            ui.column(
                7,
                ui.input_action_button(
                    "smoothing_fit_apply_on_all", "Apply on all variables", width="100%"
                ),
            ),
            ui.column(5, ui.input_action_button("smoothing_fit_reset", "Reset", width="100%")),
        ),
        ui.hr(style="margin: 4px 0;"),
        ui.h5("Outlier Removal"),
        ui.row(
            ui.column(
                3,
                ui.input_numeric(
                    "smoothing_outlier_threshold", None, value=3, min=0, max=10, step=1
                ),
            ),
            ui.column(7, ui.div("Standard deviations")),
            ui.column(2, ui.input_checkbox("smoothing_outlier_remove", None, False)),
        ),
        ui.row(
            ui.column(
                7,
                ui.input_action_button(
                    "smoothing_outlier_apply_on_all",
                    "Apply on all variables",
                    width="100%",
                ),
            ),
            ui.column(
                5,
                ui.input_action_button("smoothing_outlier_reset", "Reset", width="100%"),
            ),
        ),
        width=350,
        open="always",
    ),
    ui.div(
        ui.div("Current subject/box: "),
        ui.output_text("smoothing_plot_sample"),
        ui.input_action_button("smoothing_plot_prev", "< Prev"),
        ui.input_action_button("smoothing_plot_next", "Next >"),
        class_="calopy-row",
    ),
    output_widget("smoothing_plot", height=450),
    ui.row(
        ui.column(8),
        ui.column(
            2,
            ui.download_button("smoothed_data_downloader", "Download data", width="75%"),
            align="right",
        ),
        ui.column(
            2,
            ui.download_button("smoothed_plot_downloader", "Download PDFs", width="75%"),
            align="left",
        ),
    ),
    ui.hr(style="margin: 4px 0;"),
    ui.h6("Method overview"),
    ui.output_text_verbatim("smoothing_parameter_info"),
)
