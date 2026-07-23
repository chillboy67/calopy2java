from shiny import ui
from shinywidgets import output_widget

from calopy.maths.features import RAW_DATA

scatter_shiny = ui.layout_sidebar(
    ui.sidebar(
        "data curve comparison between different groups and direct visualization of various extracted features (for example: maximum, minimum, amplitude, AUC, ... ). through applying different modifications to the data, the results can be explored (with or without applied curve fitting, excluded samples, split into single days)",
        ui.hr(style="margin: 4px 0;"),
        ui.h4("Measurement"),
        ui.row(
            ui.input_select("scatter_measurement_no_1", "first", [], width="150px"),
            ui.input_select("scatter_feature_no_1", "first feature", [RAW_DATA], width="150px"),
        ),
        ui.row(
            ui.input_select("scatter_measurement_no_2", "second", [], width="150px"),
            ui.input_select("scatter_feature_no_2", "second feature", [RAW_DATA], width="150px"),
        ),
        ui.hr(style="margin: 4px 0;"),
        ui.input_select("scatter_grouped", "grouping", []),
        ui.hr(style="margin: 4px 0;"),
        ui.panel_conditional(
            "!['" + RAW_DATA + "'].includes(input.scatter_feature_no_1)",
            ui.input_checkbox("scatter_daysplit", "split sample into single days", False),
            ui.div("day start: d/h/m"),
            ui.row(
                ui.input_date("scatter_start_date", None, width="150px"),
                ui.input_numeric(
                    "scatter_start_time_hour",
                    None,
                    0,
                    min=0,
                    max=24,
                    step=1,
                    width="100px",
                ),
                ":",
                ui.input_numeric(
                    "scatter_start_time_minute",
                    None,
                    00,
                    min=0,
                    max=60,
                    step=1,
                    width="100px",
                ),
            ),
        ),
        width=350,
        open="always",
    ),
    ui.row(
        ui.column(6, ui.output_plot("scatter_plot_measurement_1")),
        ui.column(6, ui.output_plot("scatter_plot_measurement_2")),
    ),
    ui.output_plot("scatter_plot"),
    ui.div(ui.download_button("scatter_data_downloader", "Download scatter data")),
    output_widget("scatter_show_daysplit"),
)
