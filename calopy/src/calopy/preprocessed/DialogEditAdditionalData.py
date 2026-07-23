import pandas as pd
from shiny import reactive, render, ui

from calopy.calopy_store import calopyStore

dialogEditAdditionalData_shiny = ui.page_fluid(
    ui.head_content(ui.tags.link(rel="stylesheet", href="styles.css")),
    ui.div(ui.output_ui("dialog_edit_additional_data"), style="overflow:auto"),
    ui.div(
        ui.input_action_button("add_column", "Add Column"),
        ui.input_text("additionalData_new_column_name", None, "New Column Name"),
        class_="calopy-row",
    ),
    ui.div(
        ui.input_action_button("delete_column", "Delete Column"),
        ui.input_select("column_for_deletion", None, []),
        class_="calopy-row",
    ),
    ui.div(
        ui.input_file("file1", "Add Metadata from file", accept=[".csv"], multiple=False),
    )
)

additional_data_update_toggle = reactive.Value(True)


def additional_data_update():
    print("additional_data_update")
    additional_data_update_toggle.set(not additional_data_update_toggle())


def dialogEditAdditionalData(input, output, session):
    @output
    @render.ui
    @reactive.event(additional_data_update_toggle)
    def dialog_edit_additional_data():
        print("dialog_edit_additional_data")
        additionalData: pd.DataFrame = calopyStore(session).additionalData
        columns = []
        if additionalData is not None:
            # print(additionalData)
            index_of_box = additionalData.columns.get_loc("box")
            ui.update_select(
                "column_for_deletion",
                choices=additionalData.columns.delete(index_of_box).tolist(),
                selected=None,
            )
            columns_index = 0
            for column in additionalData.columns:
                rows = []
                rows_index = 0
                rows.append(column)
                for index, value in additionalData[column].items():
                    id = str(columns_index) + "_" + str(rows_index)
                    rows.append(ui.input_text(id, None, value=str(value), width="150px"))
                    rows_index += 1
                columns.append(ui.div(rows, class_="calopy-column"))
                columns_index += 1

        return ui.div(columns, class_="calopy-row")

    @reactive.Effect
    @reactive.event(input.delete_column)
    def delete_column():
        print("delete_column")
        column_for_deletion = input.column_for_deletion()
        calopyStore(session).additionalData.pop(column_for_deletion)
        additional_data_update()

    @reactive.Effect
    @reactive.event(input.add_column)
    def add_column():
        print("add_column")
        data = calopyStore(session).additionalData
        column_name = input.additionalData_new_column_name()

        # Error Handling
        if not column_name:
            print("Error: Column name cannot be empty.")
            return
        if column_name in data.columns:
            print(f"Error: Column '{column_name}' already exists.")
            return

        series = [column_name] * len(data)
        calopyStore(session).additionalData = pd.concat(
            [data, pd.Series(series, name=column_name, index=data.index)], axis=1
        )
        additional_data_update()


    @reactive.Effect
    @reactive.event(input.file1)
    def add_metadata_from_file():
        print("Processing uploaded file for metadata")

        uploaded_file = input.file1()
        if uploaded_file is None:
            print("No file uploaded.")
            return

        try:
            new_metadata = pd.read_csv(uploaded_file[0]["datapath"])
            print(f"Uploaded file successfully read:\n{new_metadata}")

            current_data = calopyStore(session).additionalData

            if current_data is None or current_data.empty:
                print("No existing additionalData. Setting new metadata as additionalData.")
                calopyStore(session).additionalData = new_metadata
            else:
                if "box" not in current_data.columns:
                    raise ValueError("The existing additionalData must have a 'box' column.")

                first_column_name = new_metadata.columns[0]

                # Align data types of the "box" column in both DataFrames
                current_data["box"] = current_data["box"].astype(str)
                new_metadata[first_column_name] = new_metadata[first_column_name].astype(str)

                merged_data = pd.merge(
                    current_data,
                    new_metadata,
                    left_on="box",
                    right_on=first_column_name,
                    how="left",  # Use 'left' join to keep all existing rows
                )
                print(f"Data successfully merged:\n{merged_data}")

                # Drop the redundant first column from new_metadata after the merge
                merged_data = merged_data.drop(columns=[first_column_name])

                calopyStore(session).additionalData = merged_data

            additional_data_update()
            print("additionalData successfully updated with metadata from file.")
        except Exception as e:
            print(f"Error processing uploaded file: {e}")
