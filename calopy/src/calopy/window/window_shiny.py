from shiny import ui
from shinywidgets import output_widget

ROLLING_WINDOW = "Rolling window"
NEXT_SEGMENTS = "Next segments"
ALL_SAMPLE_WINDOW = "All Sample Window"

window_analysis_shiny = ui.layout_sidebar(
    ui.sidebar(
        ui.h5("Dependent Variable"),
        ui.input_select("window_measurement_no_1", "Select metabolic variable", []),
        ui.hr(style="margin: 4px 0;"),
        ui.h5("Settings"),
        ui.input_select("window_grouped", "Select grouping/aggregation", []),
        # Currently inactivated due to errors depending on daylength settings. And not sure this is useful anyway
        #ui.input_select("day_night_restrictions", "Daytime restriction", []),
        ui.input_numeric("window_size", "Window size", value=10),
        ui.input_checkbox("overlapping_windows", "Use overlapping windows", False),
        ui.panel_conditional(
            "input.overlapping_windows",
            ui.input_numeric("timesteps_moved_by", "Window step", value=10),
        ),
        width=350,
        open="always",
    ),
    ui.row(
        ui.input_checkbox("window_swarmplot", "Show swarmplot", False),
        ui.input_checkbox("window_stat_annotations", "Show stat annotations (p-fdr)", False),
    ),
    ui.row(
        output_widget("window_plot")
        # ui.output_plot("window_plot", height = "100%"),
        # {"style": "height: 450px;"},
    ),
    ui.row(
        ui.column(
            6,
            ui.download_button("windows_data_downloader", "Download data", width="80%"),
            align="center",
        ),
        ui.column(
            6,
            ui.download_button("windows_plot_downloader", "Download plot", width="80%"),
            align="center",
        ),
    ),
    ui.row(ui.h5("Statistics"), ui.output_table("window_stat_annotations_table")),
    ui.row(ui.download_button("window_stats_downloader", "Download stats table", width="30%")),
    ui.column(
        10,
        ui.output_text_verbatim("window_stats_summary"),
    ),
    # ui.panel_conditional(
    #     "window_stat_annotations",
    #     ui.output_text_verbatim("window_stat_annotations_text"),
    # ),
)
