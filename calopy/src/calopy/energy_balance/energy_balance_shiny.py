from shiny import ui
from calopy.shared_ui.icons import question_circle_fill
from shinywidgets import output_widget

energy_balance_shiny = ui.layout_sidebar(
    ui.sidebar(
ui.h5("Energy Intake"),
        ui.tooltip(
            ui.div(ui.input_select("energy_intake_measurement", "Select Energy Intake (non cumulative)", []),
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Select energy intake variable from metabolic variables",
            placement="left"
        ),
        ui.h5("Energy Expenditure"),
        ui.tooltip(
            ui.div(ui.input_select("energy_expenditure_measurement", "Select Energy Expenditure", []),
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Select energy expenditure variable from metabolic variables",
            placement="left"
        ),
        ui.hr(style="margin: 4px 0;"),
        ui.h5("Predictive Variables"),
        ui.tooltip(
            ui.div(ui.input_select("energy_balance_group", "Select grouping/aggregation", []),
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Select categorical grouping variable for Energy Balance analyses.",
            placement="left"
        ),
        ui.tooltip(
            ui.div(ui.input_select("energy_balance_covariable", "Select covariable", []),
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Select covariable (Body Weight) for ANCOVA.",
            placement="left"
        ),
        ui.hr(style="margin: 4px 0;"),
        #ui.h5("Options"),
        #ui.input_checkbox("energy_balance_do_ancova_statistics", "do ANCOVA (needs implementation)", False),
        width=350,
        open="always",
    ),
    ui.h5("Energy Balance Plot"),
    ui.row(
        output_widget("energy_balance_combined_plot", width="99%"),
    ),
    ui.row(
        ui.column(
            8,
            ui.row(
                ui.input_checkbox("energy_balance_show_sem", "Show SEM", False),
            ),
        ),
        ui.column(
            2,
            ui.download_button("energy_balance_data_downloader", "Download data", width="75%"),
            align="right",
        ),
        ui.column(
            2,
            ui.download_button("energy_balance_plot_downloader", "Download PDF", width="75%"),
            align="left",
        ),
    ),
    ui.hr(style="margin: 4px 0;"),
    ui.h5("Energy Balance Results"),
    ui.row(
        output_widget("energy_balance_stats_plot", width="99%"),
    ),
    ui.row(
        ui.column(8),
        ui.column(
            2,
            ui.download_button("energy_balance_boxplot_data_downloader", "Download data", width="75%"),
            align="right",
        ),
        ui.column(
            2,
            ui.download_button("energy_balance_boxplot_downloader", "Download PDF", width="75%"),
            align="left",
        ),
    ),
    ui.hr(style="margin: 4px 0;"),
    ui.row(
        ui.h5("Energy Balance Statistics"),
        ui.column(4,
                  ui.card(
                      ui.card_header("ANCOVA on Energy Intake data"),
                      ui.output_table("energy_balance_stat_result_ei")
                  )
                  ),
        ui.column(4,
                  ui.card(
                      ui.card_header("ANCOVA on Energy Expenditure data"),
                      ui.output_table("energy_balance_stat_result_ee")
                  )
                  ),
        ui.column(4,
                  ui.card(
                      ui.card_header("ANOVA on Energy Balance data"),
                      ui.output_table("energy_balance_stat_result_eb")
                  )
            )
    ),
    ui.row(
        ui.download_button("energy_balance_stats_downloader", "Download complete stats tables", width="30%")
    ),
    ui.row(
        ui.column(
            10,
            ui.output_text_verbatim("energy_balance_stats_summary"),
        ),
    ),
)
