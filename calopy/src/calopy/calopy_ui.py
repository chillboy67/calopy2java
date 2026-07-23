from shiny import ui

PREPROCESSING = "Preprocessing"
SMOOTHING = "Filtering"
RMR_BMR = "RMR/BMR Estimation (experimental)"
SCATTER = "Between Variables (experimental)"
# BOX = "Box (outdated)"
# BOXNEW = 'Boxnew (outdated)'
CONDITIONS = "Temporal Conditions (Within Groups)"
WINDOW = "Time Window Comparison"
BETWEENGROUPS = "Between-Group Comparison"
ENERGYBALANCE = "Energy Balance"
DOCUMENTATION = "Documentation"
INFO = "Info & Contact"
FAQ = "FAQ"



calopy_ui = ui.page_fluid(
    ui.head_content(
      ui.tags.link(rel="stylesheet", href="styles.css"),
      ui.tags.link(rel="shortcut icon", href="favicon.ico"),
      ui.tags.title("Calopy")
    ),
    ui.row(
        ui.column(4, ui.output_image("logo_image_calopy"), align="left"),
        ui.column(4, ui.output_image("logo_image_helmholtz"), align="right", offset=4),
        {"style": "height: 100px;"},
    ),
    ui.navset_card_tab(
        ui.nav_panel(
            "Load data",
            ui.row(
                ui.column(2,
                            ui.input_select(
                            "fileformat", "Select file format",
                            ["Generic/Sable Systems", "TSE", "Columbus", "Example Data"],
                            selected="Generic/Sable Systems")

                            #------- For security reasons this is currently deactivated, check below to also uncomment download -------#
                            #ui.input_select(
                            #"fileformat", "Select file format",
                            #["Generic/Sable Systems", "TSE", "Columbus", "Calopy object", "Example Data"],
                            #selected="Generic/Sable Systems")
                          ),
                ui.column(2,
                          ui.panel_conditional(
                              "input.fileformat === 'Generic/Sable Systems'",
                              ui.input_file(
                                  "csv_file_loader",
                                  "Select CSV data file",
                                  accept=[".csv", ".tsv"],
                                  multiple=False
                              )
                          ),
                          ui.panel_conditional(
                              "input.fileformat === 'TSE'",
                              ui.input_file(
                                  "tse_file_loader",
                                  "Select indirect calorimetry data file",
                                  accept=[".tse", ".csv", ".tsv"],
                                  multiple=False
                              )
                          ),
                        ui.panel_conditional(
                              "input.fileformat === 'Columbus'",
                              ui.input_file(
                                  "columbus_file_loader",
                                  "Select indirect calorimetry data file",
                                  accept=[".xlsx", ".csv", ".tsv"],
                                  multiple=False
                              )
                          ),

                         ui.panel_conditional(
                              "input.fileformat === 'Calopy object'",
                              ui.input_file(
                                  "calistore_file_loader",
                                  "Select Calopy object data file",
                                  accept=[".pkl"],
                                  multiple=False
                              )
                          ),

                          ui.panel_conditional(
                              "input.fileformat === 'Example Data'",
                              ui.br(),
                              ui.input_action_button("load_test_data", "Load example data")
                          ),
                          ),
                ui.column(2),  # Empty column for spacing
                ui.column(2,
                          ui.panel_conditional(
                              "input.fileformat === 'Generic/Sable Systems' | input.fileformat === 'Example Data' ",
                              ui.row("Download example data file"),
                              ui.row(
                                  ui.download_button("download_example_data", "Download", class_="btn-primary")
                              )
                          ),
                          ui.panel_conditional(
                              "input.fileformat === 'Calopy object'",
                              ui.p("CAUTION:",ui.br(),"Only load Calopy objects from sources you trust! Pickle objects can be prone to security risks.", style="color: darkred;")
                          )
                          ),
            ),
        ),
        ui.nav_panel(
            "Download data",
            ui.row(
                ui.column(
                    2,
                    ui.div(
                        ui.download_button(
                            "calopy_metabolic_variables_downloader",
                            "Download IC data file",
                            align="left",
                        )
                    ),
                ),
                ui.column(
                    2,
                    ui.div(
                        ui.download_button(
                            "calopy_metadata_downloader",
                            "Download Metadata file",
                            align="left",
                        )
                    ),
                ),
                ui.column(
                    2,
                    ui.div(
                        ui.download_button(
                            "calopy_settings_downloader",
                            "Download Settings file",
                            align="left",
                        )
                    ),
                ),
                #------- For security reasons this is deactivated, check above to also uncomment loader -------#
                # ui.column(
                #     2,
                #     ui.div(
                #         ui.download_button(
                #             "tse_calistore_downloader",
                #             "Download Calopy file",
                #             align="left",
                #         )
                #     ),
                # ),
            ),
        ),
        ui.nav_panel(
            'Help',
            ui.column(
                2,
                ui.download_button("download_howto_top", "Download HowTo", class_="btn-primary", align="right"),
            )
        ),
        id="navset_card_tab",
        selected="Load data",
    ),
    ui.navset_pill_list(
        ui.nav_control(ui.h6("Data Processing")),
        ui.nav_panel(PREPROCESSING, ui.output_ui("preprocessed_ui")),
        ui.nav_panel(SMOOTHING, ui.output_ui("smoothing_ui")),
        ui.nav_panel(RMR_BMR, ui.output_ui("rmr_ui")),
        ui.nav_control(ui.hr()),
        ui.nav_control(ui.h6("Data Analysis")),
        ui.nav_panel(BETWEENGROUPS, ui.output_ui("between_groups_ui")),
        ui.nav_panel(CONDITIONS, ui.output_ui("conditions_ui")),
        ui.nav_panel(WINDOW, ui.output_ui("window_ui")),
        ui.nav_panel(ENERGYBALANCE, ui.output_ui("energy_balance_ui")),
        # ui.nav_panel(SCATTER, ui.output_ui("scatter_ui")),
        # ui.nav_panel(BOX, ui.output_ui("box_ui")),
        ui.nav_control(ui.hr()),
        ui.nav_control(ui.h6("Help")),
        ui.nav_panel(INFO, ui.output_ui("about_calopy_ui")),
        ui.nav_panel(DOCUMENTATION, ui.output_ui("documentation_ui")),
        ui.nav_panel(FAQ, ui.output_ui("faq_calopy_ui")),
        id="selected_feature",
        widths=(2, 10),
    ),
)
