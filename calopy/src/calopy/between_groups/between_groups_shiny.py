from shiny import ui
from calopy.shared_ui.icons import question_circle_fill
from shinywidgets import output_widget

between_groups_shiny = ui.layout_sidebar(
    ui.sidebar(
        ui.h5("Dependent Variable"),
        ui.tooltip(
            ui.div(ui.input_select("between_groups_measurement_no_1", "Select metabolic variable", []),
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Select dependent variable from metabolic variables or continuous metadata",
            placement="left"
        ),
        ui.tooltip(
            ui.div(ui.input_select("light_dark_selection", "Filter light/dark phase", ["total", "light", "dark"],
                                   selected="total"),
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Define pre filter to only include data from light or dark phase or total, Also affects predictive co-variable if regression is selected",
            placement="left"
        ),
        ui.tooltip(
            ui.div(ui.input_select("raw_feature", "Select feature", []),
                    style="display: inline-flex; align-items: center;",
                    placement="left"
                    ),
            "Select data feature (dependent variable only): mean, median, maxima... See docs for detailed explanation",
            placement="left"
        ),
        ui.hr(style="margin: 4px 0;"),
        ui.h5("Predictive Variable"),
        ui.tooltip(
            ui.div(ui.input_select("between_groups_grouped", "Select grouping/aggregation", []),
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Select categorical grouping variable for ANOVA or ANCOVA analyses.",
            placement="left"
        ),
        ui.hr(style="margin: 4px 0;"),
        ui.h5("Options"),
        ui.tooltip(
            ui.div(ui.input_checkbox("use_welch", "Use Welch ANOVA", False),
                   question_circle_fill,
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Perform Welch ANOVA. More robust for unequal variances. Currently for 1-way ANOVA only",
            placement="left"
        ),
        ui.tooltip(
            ui.div(ui.input_checkbox("use_2wayfactor", "Use 2-way ANOVA", False),
                   question_circle_fill,
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Add second grouping/aggregation factor for 2-way-ANOVA.",
            placement="left"
        ),
        ui.panel_conditional(
            "input.use_2wayfactor",
            ui.input_select("between_groups_2way_factor", "2nd grouping/aggregation", []),
        ),
        ui.tooltip(
            ui.div(ui.input_checkbox("between_groups_night_and_day", "Compare light/dark", False),
                   question_circle_fill,
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Split data to day and night to perform 2 way ANOVA on selected variable (only ANOVA comparisons).",
            placement="left"
        ),
        ui.tooltip(
            ui.div(ui.input_checkbox("use_covariable", "Use linear model", False),
                   question_circle_fill,
                   style="display: inline-flex; align-items: center;",
                   placement="left"
                   ),
            "Add a covariate for either ANCOVA or regression analysis. ANCOVA is used when a grouping variable is selected (e.g., to compare EE between groups), while regression is performed if no grouping variable is specified.",
            placement="left"
        ),
        ui.panel_conditional(
            "input.use_covariable",
            ui.input_select("between_groups_measurement_no_2", "Select covariable", []),
            ui.input_select("raw_feature2", "Select feature", []),
            ui.h6("Regression Options"),
            ui.tooltip(
                ui.div(ui.input_checkbox("show_regression", "Show residuals", False),
                       question_circle_fill,
                       style="display: inline-flex; align-items: center;",
                       placement="left"
                       ),
                "Show regression residual histogram. ONLY regression NOT ANCOVA.",
                placement="left"
            ),
            ui.tooltip(
                ui.div(ui.input_checkbox("ancova_full_model", "Test full model", False),
                       question_circle_fill,
                       style="display: inline-flex; align-items: center;",
                       placement="left"
                       ),
                "Test full linear model including interaction term to test if indepencence of predictive variables for ANCOVA is violated (ANCOVA ONLY).",
                placement="left"
            ),
        ),
        width=350,
        open="always",
    ),
    ui.h5("Dependent Variable"),
    ui.row(
        output_widget("between_groups_plot_measurement_1", width="99%"),
    ),
    ui.row(
        ui.column(
            8,
            ui.row(
                ui.input_checkbox("between_groups_show_feature", "Show feature", False),
            ),
            ui.row(
                ui.input_checkbox("between_groups_show_SEM", "Show standard error", False),
            ),
        ),
        ui.column(
            2,
            ui.download_button("betweengroups_data1_downloader", "Download data", width="75%"),
            align="right",
        ),
        ui.column(
            2,
            ui.download_button("betweengroups_plot1_downloader", "Download PDF", width="75%"),
            align="left",
        ),
    ),
    ui.hr(style="margin: 4px 0;"),
    ui.h5("Results"),
    ui.row(
        ui.column(
            5,
            # ui.output_plot("between_groups_plot", width='80%'),
            output_widget("between_groups_plot", width="100%"),
        ),
        ui.column(
            5,
            ui.panel_conditional(
                "input.show_regression",
                output_widget("regression_residual_plot", width="100%"),
            ),
        ),
    ),
    ui.row(
        ui.column(1),
        ui.column(
            2,
            ui.download_button("betweengroups_data2_downloader", "Download data", width="75%"),
            align="center",
        ),
        ui.column(
            2,
            ui.download_button("betweengroups_plot2_downloader", "Download PDF", width="75%"),
            align="center",
        ),
        ui.column(6),
    ),
    ui.hr(style="margin: 4px 0;"),
    ui.row(ui.h5("Statistics"), ui.output_table("between_groups_stat_result")),
    ui.row(
        ui.download_button("betweengroups_stats_downloader", "Download stats table", width="30%")
    ),
    ui.column(
        10,
        ui.output_text_verbatim("between_groups_stats_summary"),
    ),
)
