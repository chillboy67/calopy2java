from shiny import ui
from shinywidgets import output_widget

from calopy.maths.features import get_input_selectize_feature_func_dict

conditions_shiny = ui.layout_sidebar(
    ui.sidebar(
        # "compares features of selected measurement for the same samples under different conditions, e.g. before and after treatment. thus a repeated measurement ANOVA can be applied.",
        ui.h5("Dependent Variable"),
        ui.input_select("conditions_measurement", "Select metabolic variable", []),
        ui.input_select(
            "conditions_feature",
            "Select feature",
            choices=get_input_selectize_feature_func_dict(),
        ),
        ui.hr(style="margin: 4px 0;"),
        ui.h5("Conditional Variables"),
        ui.input_select("conditions_grouped", "Select grouping/aggregation", []),
        ui.h6("Temporal conditions"),
        ui.input_action_button("conditions_edit", "Edit conditions"),
        ui.div(ui.output_table("conditions_list"), style="overflow:auto"),
        width=350,
        open="always",
    ),
    ui.h5("Dependent Variable"),
    ui.row(
        output_widget("between_conditions_data_plot", width="99%"),
    ),
    ui.row(
        ui.column(
            8,
            ui.input_checkbox("conditions_showpeak", "Show feature", False),
            ui.input_checkbox("conditions_show_SEM", "Show standard error", False),
        ),
        ui.column(
            2,
            ui.download_button("conditions_data1_downloader", "Download data", width="75%"),
            align="right",
        ),
        ui.column(
            2,
            ui.download_button("conditions_plot1_downloader", "Download PDF", width="75%"),
            align="left",
        ),
    ),
    ui.hr(style="margin: 4px 0;"),
    ui.h5("Result"),
    ui.row(
        output_widget("conditions_plot", width="40%"),
    ),
    ui.row(
        ui.column(
            2,
            ui.download_button("condition_sliced_data_download", "Download data", width="75%"),
            align="right",
        ),
        ui.column(
            2,
            ui.download_button("conditions_stats_plot_downloader", "Download PDF", width="75%"),
            align="right",
        ),
    ),
    ui.row(ui.output_table("conditions_stat_result")),
    ui.row(ui.download_button("condition_stats_downloader", "Download stats table", width="30%")),
    ui.column(
        10,
        ui.output_text_verbatim("conditions_stats_summary"),
    ),
)
