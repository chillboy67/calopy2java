import pandas as pd
from shiny import reactive, render, ui
from calopy.calopy_store import caliData, calopyStore
from calopy.maths.series_utils import get_time_sampling_interval_for_variable


dialogEditMetabolicVariable_shiny = ui.page_fluid(
    ui.head_content(ui.tags.link(rel="stylesheet", href="styles.css")),
    ui.h5("Add Energy Intake"),
    ui.div(
        ui.input_select("energy_intake_variable", "Select Food Intake (non-cumulative)", choices=[]),
        ui.input_select("diet_kcal_g", "Select Diet (kcal/g)", choices=[]),
        ui.input_text("EnergyIntake_variable_name", "New variable name", "Energy Intake (kcal/h)"),
        ui.input_action_button("add_energy_intake", "Add", class_="btn-primary"),
        class_="calopy-row",
    ),
)

metabolic_variable_update_toggle = reactive.Value(True)

def metabolic_variable_update():
    print("metabolic_variable_update")
    metabolic_variable_update_toggle.set(not metabolic_variable_update_toggle())

def dialogEditMetabolicVariable(input, output, session):
    @reactive.Effect
    @reactive.event(metabolic_variable_update_toggle)
    def update_dropdowns():
        print("Adding dropdowns to the add/edit Metabolic Variable")
        try:
            metvariables = caliData(session).measurements()
            addvariables = caliData(session).getContinuousColumns()
            ui.update_select("energy_intake_variable", choices=metvariables)
            ui.update_select("diet_kcal_g", choices=addvariables)
        except Exception as e:
            print(f"Error updating dropdowns in metabolic variable dialog: {e}")

    @reactive.Effect
    @reactive.event(input.add_energy_intake)
    def add_energy_intake():
        print("Adding energy intake")
        if caliData(session) is not None:
            feed_cumulative_variable = input.energy_intake_variable()
            selected_diet = input.diet_kcal_g()
            
            if feed_cumulative_variable and selected_diet:
                energy_intake_var_name = input.EnergyIntake_variable_name()
                food_intake_data = caliData(session).measurementFilteredGroupedDateTimeIndexed(feed_cumulative_variable)
                diet_value = caliData(session).additionalData[["box", selected_diet]]

                # if diet_value.iloc[0] == 'add_value': # should be non numerical here!!!
                #     ui.notification_show("Error: Diet value is not set. Please set a numeric value in the metadata.",
                #                          type="error")
                #     return

                delta_time = get_time_sampling_interval_for_variable(food_intake_data)
                # Make sure box column in df2 is string if columns in df1 are strings
                diet_value["box"] = diet_value["box"].astype(str)
                # Create a Series: index = column names of df1, values = corresponding weights
                diet_weights = diet_value.set_index("box")[selected_diet]
                # Reorder weights to match columns in df1
                diet_weights = diet_weights[food_intake_data.columns.astype(str)]
                food_intake_data_minute = food_intake_data.div(delta_time, axis=0)
                energy_intake_kcal_min = food_intake_data_minute.multiply(diet_weights, axis=1)
                energy_intake_kcal_hr = energy_intake_kcal_min.multiply(60, axis=0)

                caliData(session).add_measurement_to_data(energy_intake_kcal_hr, energy_intake_var_name)

                ui.notification_show("Energy Intake added successfully", type="message")
                print("Energy intake added successfully")

