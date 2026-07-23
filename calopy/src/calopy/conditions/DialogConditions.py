from shiny import reactive, render, ui

from calopy.calopy_store import CONDITIONS_CONDITIONS, caliData, caliState

TO = "to"
FROM = "from"
TEXT = "Condition"

dialogConditions_shiny = ui.page_fluid(
    ui.head_content(ui.tags.link(rel="stylesheet", href="styles.css")),
    ui.div(ui.output_ui("dialog_edit_conditions"), style="overflow:auto"),
    ui.row(
        ui.column(6, ui.input_action_button("conditions_add", "add condition")),
        ui.column(2, ui.column(3, ui.input_action_button("conditions_remove", "remove"))),
        ui.column(4, ui.input_select("conditions_remove_select", None, [])),
    ),
)

dialog_conditions_update_toggle = reactive.Value(True)


def dialog_conditions_update():
    print("additional_data_update")
    dialog_conditions_update_toggle.set(not dialog_conditions_update_toggle())


def dialogConditions(input, output, session):
    @output
    @render.ui
    @reactive.event(dialog_conditions_update_toggle)
    def dialog_edit_conditions():
        conditions = caliState(session)[CONDITIONS_CONDITIONS]
        listOfConditions = []
        for i, condition in enumerate(conditions):
            listOfConditions.append(
                ui.div(
                    ui.input_text("conditions_text_" + str(i), None, value=condition[TEXT]),
                    ui.row(
                        ui.input_date(
                            "conditions_start_date_" + str(i),
                            None,
                            value=condition[FROM].date(),
                            width="150px",
                        ),
                        ui.input_numeric(
                            "conditions_start_time_hour_" + str(i),
                            None,
                            value=condition[FROM].time().hour,
                            min=0,
                            max=24,
                            step=1,
                            width="100px",
                        ),
                        ":",
                        ui.input_numeric(
                            "conditions_start_time_minute_" + str(i),
                            None,
                            value=condition[FROM].time().minute,
                            min=0,
                            max=60,
                            step=1,
                            width="100px",
                        ),
                    ),
                    ui.row(
                        ui.input_date(
                            "conditions_end_date_" + str(i),
                            None,
                            value=condition[TO].date(),
                            width="150px",
                        ),
                        ui.input_numeric(
                            "conditions_end_time_hour_" + str(i),
                            None,
                            value=condition[TO].time().hour,
                            min=0,
                            max=24,
                            step=1,
                            width="100px",
                        ),
                        ":",
                        ui.input_numeric(
                            "conditions_end_time_minute_" + str(i),
                            None,
                            value=condition[TO].time().minute,
                            min=0,
                            max=60,
                            step=1,
                            width="100px",
                        ),
                    )
                )
            )
        ui.update_select(
            "conditions_remove_select",
            choices=list(map(lambda it: it[TEXT], conditions)),
        )

        return ui.div(listOfConditions)

    @reactive.Effect
    @reactive.event(input.conditions_remove)
    def removeCondition():
        conditions = caliState(session)[CONDITIONS_CONDITIONS]
        index = list(map(lambda it: it[TEXT], conditions)).index(input.conditions_remove_select())
        conditions.pop(index)
        dialog_conditions_update()

    @reactive.Effect
    @reactive.event(input.conditions_add)
    def addCondition():
        conditions = caliState(session)[CONDITIONS_CONDITIONS]
        conditions.append(
            {
                TEXT: "Condition " + str(len(conditions) + 1),
                FROM: caliData(session).croppedStart,
                TO: caliData(session).croppedEnd,
            }
        )
        dialog_conditions_update()
