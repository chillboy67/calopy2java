from shiny import ui
from shinywidgets import output_widget

Documentation_shiny = ui.navset_pill_list(
    ui.nav_panel("Introduction", ui.output_ui("introduction")),
    ui.nav_panel("Data Types", ui.output_ui("datatypes")),
    ui.nav_panel("Data Format", ui.output_ui("dataformat")),
    ui.nav_panel("Preprocessing", ui.output_ui("preprocessing")),
    ui.nav_panel("Filtering", ui.output_ui("filtering")),
    ui.nav_panel("BMR/RMR Estimation", ui.output_ui("BMR_RMR")),
    ui.nav_panel("Data Analysis", ui.output_ui("dataanalysis")),
    id="doc_tabs",
    widths=(2, 10),
)
