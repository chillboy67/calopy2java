from shiny import ui
from shinywidgets import output_widget

rmr_shiny = ui.layout_sidebar(
    ui.sidebar(
        ui.h5("Model Selection"),
        ui.input_select("Model", "", choices=["None", "RMR only", "BMR/RMR"]),
        ui.h6("Select variables for BMR/RMR estimation:"),
        ui.panel_conditional(
            "input.Model === 'None'",
            ui.h6("Please select model first!"),
        ),
        ui.panel_conditional(
            "input.Model !== 'None'",
            ui.input_select("rmr_measurement_no_1", "Energy expenditure", []),
            ui.input_select("rmr_measurement_no_2", "Activity", []),
            # ui.input_select("rmr_measurement_no_3", "food intake (non cumulative)", []),
        ),
        ui.panel_conditional(
            "input.Model === 'BMR/RMR'",
            # ui.input_select("rmr_measurement_no_1", "energy expenditure", []),
            # ui.input_select("rmr_measurement_no_2", "activity", []),
            ui.input_select("rmr_measurement_no_3", "food intake (non cumulative)", []),
        ),
        ui.panel_conditional(
            "input.Model !== 'None'",
            ui.input_action_button("rmr_initialize_rmr_bmr", "Add/update RMR/BMR"),
        ),
        width=350,
        open="always",
    ),
    ui.div(
        ui.div("Current subject/box: "),
        ui.output_text("rmr_sample"),
        ui.input_action_button("rmr_prev", "< Prev"),
        ui.input_action_button("rmr_next", "Next >"),
        class_="calopy-row",
    ),
    output_widget("rmr_plot", height=990),
    #output_widget("rmr_plot", render_fn=render_plotly, height="990px"),
    ui.row(
        # ui.column(2, ui.download_button("condition_sliced_data_download", "Download data", width="75%"),  align="right"),
        ui.column(
            2,
            ui.download_button("rmr_bmr_plot_downloader", "Download PDF", width="75%"),
            align="right",
        ),
    ),
    ui.input_checkbox("show_reg_table", "Show regression results table", False),
    ui.panel_conditional(
    "input.show_reg_table",
    ui.div(
        ui.row(ui.output_table("show_rmr_bmr_table"))
        )),
)
