import datetime
import io

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from shiny import reactive, render, ui
from shinywidgets import render_widget, render_plotly


from calopy.calopy_store import caliData
from calopy.calopy_ui import RMR_BMR
from calopy.maths.series_utils import find_label_in_list, getAreasWhereDatetimIndexIs, \
                                      getIndexOf24HourInterval
from calopy.maths.statistic import calopy_regression, linear_regression, rmr_without_activity_data
from calopy.rmr.rmr_shiny import rmr_shiny
from calopy.shared_ui.plot_config import COLOR_DATECHANGE, COLOR_NIGHTTIME, create_empty_plot, \
                                         get_color_samples
from calopy.calopy_store import calopyStore

def rmr(input, output, session):
    rmr_update_toggle = reactive.Value(True)
    # model_name= 'RMR only'
    model_name = "None"

    rmr_measurement_no_1 = "h(3)"
    rmr_measurement_no_2 = "xt+yt"
    rmr_measurement_no_3 = "feed"

    rmr_seriesToShow = reactive.Value(0)

    def rmr_update():
        print("rmr_update_ui")
        rmr_update_toggle.set(not rmr_update_toggle())

    @output
    @render.ui
    def rmr_ui():
        print("rmr_ui")
        return rmr_shiny

    @reactive.Effect
    @reactive.event(input.selected_feature)
    def rmr_selected_feature():
        print("selected_feature")
        if input.selected_feature() == RMR_BMR:
            rmr_load_state()
            rmr_update()

    def rmr_load_state():
        print("rmr_load_state")
        try:
            ui.update_select("Model", choices=["None", "RMR only", "BMR/RMR"], selected=model_name)
            ui.update_select(
                "rmr_measurement_no_1",
                choices=caliData(session).measurements(),
                selected=find_label_in_list(
                    caliData(session).measurements(), rmr_measurement_no_1
                ),
            )
            ui.update_select(
                "rmr_measurement_no_2",
                choices=caliData(session).measurements(),
                selected=find_label_in_list(
                    caliData(session).measurements(), rmr_measurement_no_2
                ),
            )
            ui.update_select(
                "rmr_measurement_no_3",
                choices=caliData(session).measurements(),
                selected=find_label_in_list(
                    caliData(session).measurements(), rmr_measurement_no_3
                ),
            )
        except Exception as e:
            print("rmr_load_state failed")
            print(e)

    def rmr_save_state():
        print("rmr_save_state")
        nonlocal rmr_measurement_no_1
        rmr_measurement_no_1 = input.rmr_measurement_no_1()
        nonlocal rmr_measurement_no_2
        rmr_measurement_no_2 = input.rmr_measurement_no_2()
        nonlocal rmr_measurement_no_3
        rmr_measurement_no_3 = input.rmr_measurement_no_3()
        nonlocal model_name
        model_name = input.Model()

    @reactive.Effect
    @reactive.event(
        input.rmr_measurement_no_1,
        input.rmr_measurement_no_2,
        input.rmr_measurement_no_3,
        input.Model,
    )
    def update_rmr():
        rmr_save_state()
        rmr_update()

    def rmr_get_rmr_bmr_all():
        model_name = input.Model()
        energy_expenditure = caliData(session).measurementDateTimeIndexed(
            input.rmr_measurement_no_1()
        )
        activity = caliData(session).measurementDateTimeIndexed(input.rmr_measurement_no_2())
        food = caliData(session).measurementDateTimeIndexed(input.rmr_measurement_no_3())

        rmr_df = energy_expenditure.copy().fillna(pd.NA)
        bmr_df = energy_expenditure.copy().fillna(pd.NA)

        additional_data = caliData(session).additionalData.copy()

        if model_name == "BMR/RMR":
            necessary_columns = ["beta_cca2", "beta_tef", "BMR_intercept"]
        elif model_name == "RMR only":
            necessary_columns = ["beta_cca1", "RMR_intercept"]
        else:
            necessary_columns = []

        for col in necessary_columns:
            if col not in additional_data.columns:
                additional_data[col] = pd.NA

        additional_data["box"] = additional_data["box"].astype(str)

        for box in energy_expenditure.columns:
            try:
                rmr_bmr_dict = rmr_calculate_rmr_bmr_sample(
                    model_name=model_name,
                    energy_expenditure=energy_expenditure[box],
                    activity=activity[box],
                    food=food[box],
                )
                rmr_df[box] = rmr_bmr_dict.get("rmr")
                bmr_df[box] = rmr_bmr_dict.get("bmr")

                box_str = str(box)
                if box_str in additional_data["box"].astype(str).values:
                    idx = additional_data[additional_data["box"].astype(str) == box_str].index[0]
                    caliData(session).setAdditionalData(additional_data)
                    for col in necessary_columns:
                        coef_value = rmr_bmr_dict.get(col, pd.NA)
                        additional_data.at[idx, col] = coef_value
                        print(f"Assigned {col} for box {box}: {coef_value}")
                else:
                    print(f"Box {box} not found in additional_data")

            except Exception as e:
                print(f"Error processing box {box}: {e}")
        return {"rmr": rmr_df, "bmr": bmr_df}

    def rmr_calculate_rmr_bmr_sample(
        model_name, energy_expenditure=None, activity=None, food=None
    ):
        try:
            if model_name == "None":
                return {}

            if model_name == "BMR/RMR":
                if not (
                    energy_expenditure.index.equals(activity.index)
                    and energy_expenditure.index.equals(food.index)
                ):
                    raise ValueError(
                        "Indices of energy_expenditure, activity, and food do not match."
                    )

                mdl = calopy_regression(
                    pd.concat([activity.rename("activity"), food.rename("food")], axis=1),
                    energy_expenditure,
                )

                if mdl is None or len(mdl["coef"]) < 3:
                    raise ValueError("Failed to compute coefficients for BMR/RMR model.")

                beta_cca2, beta_tef = round(mdl["coef"][1], 5), round(mdl["coef"][2], 5)
                bmr_rmr_intercept = round(mdl["coef"][0], 5)

                print(f"calculated bmr_rmr_intercept={bmr_rmr_intercept}")
                print(f"Calculated coefficients: beta_cca2={beta_cca2}, beta_tef={beta_tef}")
                rmr = energy_expenditure.subtract(activity * beta_cca2)
                bmr = rmr.subtract(food * beta_tef)
                return {
                    "bmr": bmr,
                    "rmr": rmr,
                    "beta_cca2": beta_cca2,
                    "beta_tef": beta_tef,
                    "BMR_intercept": bmr_rmr_intercept,
                }

            elif model_name == "RMR only":
                if not energy_expenditure.index.equals(activity.index):
                    raise ValueError("Indices of energy_expenditure and activity do not match.")

                model = calopy_regression(activity, energy_expenditure)
                if model is None or len(model["coef"]) < 2:
                    raise ValueError("Failed to compute coefficients for RMR only model.")

                beta_cca1, intercept = round(model["coef"][1], 5), round(model["coef"][0], 5)
                print(f"Calculated coefficients: beta_cca1={beta_cca1}, intercept={intercept}")
                rmr = energy_expenditure.subtract(activity * beta_cca1)
                return {
                    "rmr": rmr,
                    "predicted_rmr": activity * beta_cca1 + intercept,
                    "beta_cca1": beta_cca1,
                    "RMR_intercept": intercept,
                }

            elif model_name == "RMR MK":
                # TODO: Implement the RMR MK model calculation
                pass

        except Exception as e:
            print(f"Error in rmr_calculate_rmr_bmr_sample: {e}")
            return {}

    @reactive.Effect
    @reactive.event(input.rmr_initialize_rmr_bmr)
    def rmr_initialize_rmr_bmr():
        if caliData(session) is not None:
            rmr_bmr_dict = rmr_get_rmr_bmr_all()
            caliData(session).add_measurement_to_data(rmr_bmr_dict["rmr"], "rmr_estimate")
            caliData(session).add_measurement_to_data(rmr_bmr_dict["bmr"], "bmr_estimate")
            rmr_update()

    @output(id="rmr_plot")
    @render_plotly
    @reactive.event(rmr_update_toggle)
    def rmr_plot_wrapper():
        return rmr_plot()

    def rmr_plot():
        print("rmr_plot")
        
        try:
            model_name = input.Model()
            energy_expenditure_all = caliData(session).measurementDateTimeIndexed(
                input.rmr_measurement_no_1()
            )
            activity_all = caliData(session).measurementDateTimeIndexed(input.rmr_measurement_no_2())
            intake_all = caliData(session).measurementDateTimeIndexed(input.rmr_measurement_no_3())
            spans = getAreasWhereDatetimIndexIs(
                energy_expenditure_all,
                lambda x: not caliData(session).night > x.time() > caliData(session).day,
            )
    
            ### make all files start on 1st january to show day 1 instead of exact date in plot
            days_difference = (
                pd.Timestamp("2018-01-01").date() - energy_expenditure_all.index[0].date() 
            ).days -1
            if caliData(session).plotXlabelDay == "day":
                energy_expenditure_all.index = energy_expenditure_all.index + pd.DateOffset(
                    days=days_difference
                )
                activity_all.index = activity_all.index + pd.DateOffset(days=days_difference)
                intake_all.index = intake_all.index + pd.DateOffset(days=days_difference)
                spans = [
                    (
                        start + pd.DateOffset(days=days_difference),
                        end + pd.DateOffset(days=days_difference),
                    )
                    for start, end in spans
                ]
    
            energy_expenditure = filtering(energy_expenditure_all)
            activity = filtering(activity_all)
            intake = filtering(intake_all)
    
            y_limit_range_ee = [
                min(energy_expenditure_all.min()),
                max(energy_expenditure_all.max()),
            ]
            y_limit_range_act = [min(activity_all.min()), max(activity_all.max())]
            y_limit_range_intake = [min(intake_all.min()), max(intake_all.max())]
            x_axis_values = energy_expenditure_all.index
            x_limit_range = [
                energy_expenditure_all.index[0],
                energy_expenditure_all.index[-1],
            ]
            all_measurements = caliData(session).measurements()
            col_pal = get_color_samples(["1_ee", "3_rmr", "2_bmr", "5_food", "4_act"])
    
            if (
                model_name == "BMR/RMR"
                and "bmr_estimate" in all_measurements
                and "rmr_estimate" in all_measurements
            ):
    
                rmr_series_all = caliData(session).measurementDateTimeIndexed("rmr_estimate")
                rmr_series_smooth = filtering(
                    caliData(session).measurementFilteredDateTimeIndexed("rmr_estimate")
                )
                bmr_series_all = caliData(session).measurementDateTimeIndexed("bmr_estimate")
                bmr_series_smooth = caliData(session).measurementFilteredDateTimeIndexed(
                    "bmr_estimate"
                )
    
                if caliData(session).plotXlabelDay == "day":
                    rmr_series_all.index = rmr_series_all.index + pd.DateOffset(days=days_difference)
                    rmr_series_smooth.index = rmr_series_smooth.index + pd.DateOffset(
                        days=days_difference
                    )
                    bmr_series_all.index = bmr_series_all.index + pd.DateOffset(days=days_difference)
                    bmr_series_smooth.index = bmr_series_smooth.index + pd.DateOffset(
                        days=days_difference
                    )
    
                rmr_series = filtering(rmr_series_all)
                bmr_series = filtering(bmr_series_all)
                bmr_series_smooth = filtering(bmr_series_smooth)
                y_limit_range_ee_bmr = [min(bmr_series_all.min()), y_limit_range_ee[1]]
    
                fig = make_subplots(
                    rows=3,
                    cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    row_heights=[0.44, 0.28, 0.28],
                    subplot_titles=("Energy Expenditure", "Activity", "Food intake"),
                )
    
                fig.add_trace(
                    go.Scatter(
                        y=energy_expenditure,
                        x=x_axis_values,
                        showlegend=True,
                        name="TEE",
                        marker_color=col_pal["1_ee"],
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        y=rmr_series,
                        x=x_axis_values,
                        showlegend=True,
                        mode="markers",
                        name="RMR points",
                        marker=dict(color=col_pal["3_rmr"], opacity=0.7, size=5),
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        y=rmr_series_smooth,
                        x=x_axis_values,
                        showlegend=True,
                        name="RMR fitted",
                        marker_color=col_pal["3_rmr"],
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        y=bmr_series,
                        x=x_axis_values,
                        showlegend=True,
                        mode="markers",
                        name="BMR points",
                        marker=dict(color=col_pal["2_bmr"], opacity=0.7, size=5),
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        y=bmr_series_smooth,
                        x=x_axis_values,
                        showlegend=True,
                        name="BMR fitted",
                        marker_color=col_pal["2_bmr"],
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        y=activity,
                        x=x_axis_values,
                        showlegend=False,
                        marker_color=col_pal["4_act"],
                    ),
                    row=2,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        y=intake,
                        x=x_axis_values,
                        showlegend=False,
                        marker_color=col_pal["5_food"],
                    ),
                    row=3,
                    col=1,
                )
    
                fig.update_yaxes(
                    title_text="Energy Expenditure",
                    range=y_limit_range_ee_bmr,
                    row=1,
                    col=1,
                )
                fig.update_yaxes(
                    title_text=input.rmr_measurement_no_2(),
                    range=y_limit_range_act,
                    row=2,
                    col=1,
                )
                fig.update_yaxes(
                    title_text=input.rmr_measurement_no_3(),
                    range=y_limit_range_intake,
                    row=3,
                    col=1,
                )
                fig.update_xaxes(title_text="Time", range=x_limit_range, row=3, col=1)
    
            elif model_name == "RMR only" and "rmr_estimate" in all_measurements:
    
                rmr_series_all = caliData(session).measurementDateTimeIndexed("rmr_estimate")
                rmr_series_smooth = caliData(session).measurementFilteredDateTimeIndexed(
                    "rmr_estimate"
                )
    
                if caliData(session).plotXlabelDay == "day":
                    rmr_series_all.index = rmr_series_all.index + pd.DateOffset(days=days_difference)
                    rmr_series_smooth.index = rmr_series_smooth.index + pd.DateOffset(
                        days=days_difference
                    )
    
                rmr_series = filtering(rmr_series_all)
                rmr_series_smooth = filtering(rmr_series_smooth)
    
                y_limit_range_ee_rmr = [min(rmr_series_all.min()), y_limit_range_ee[1]]
                regression_result = rmr_calculate_rmr_bmr_sample(
                    model_name, energy_expenditure, activity
                )
                predicted_rmr = regression_result["predicted_rmr"]
                fig = make_subplots(
                    rows=3,
                    cols=2,
                    specs=[[{"colspan": 2}, None], [{"colspan": 2}, None], [{}, {}]],
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    row_heights=[0.33, 0.33, 0.33],
                    subplot_titles=("Energy Expenditure", "Activity", "Regression"),
                )
    
                fig.add_trace(
                    go.Scatter(
                        y=energy_expenditure,
                        x=x_axis_values,
                        showlegend=True,
                        name="TEE",
                        marker_color=col_pal["1_ee"],
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        y=rmr_series,
                        x=x_axis_values,
                        showlegend=True,
                        mode="markers",
                        name="RMR points",
                        marker=dict(color=col_pal["3_rmr"], opacity=0.7, size=5),
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        y=rmr_series_smooth,
                        x=x_axis_values,
                        showlegend=True,
                        name="RMR fitted",
                        marker_color=col_pal["3_rmr"],
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        y=activity,
                        x=x_axis_values,
                        showlegend=False,
                        marker_color=col_pal["4_act"],
                    ),
                    row=2,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=activity,
                        y=energy_expenditure,
                        mode="markers",
                        showlegend=False,
                        name="Activity vs EE",
                        marker_color=col_pal["4_act"],
                    ),
                    row=3,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=activity,
                        y=predicted_rmr,
                        mode="lines",
                        showlegend=True,
                        name="Activity vs EE Regression Line",
                        marker=dict(color="blue"),
                    ),
                    row=3,
                    col=1,
                )
                fig.add_annotation(
                    x=0.66,
                    y=0.33,
                    showarrow = False,
                    text="beta_cca1 = " + str(regression_result["beta_cca1"]) + "<br>Intercept = " + str(regression_result["RMR_intercept"]),
                    xref='x domain',
                    yref='paper',
                    row=3,
                    col=1,
                )

                fig.update_yaxes(
                    title_text="Energy Expenditure",
                    range=y_limit_range_ee_rmr,
                    row=1,
                    col=1,
                )
                fig.update_yaxes(
                    title_text=input.rmr_measurement_no_2(),
                    range=y_limit_range_act,
                    row=2,
                    col=1,
                )
                fig.update_yaxes(title_text="Energy Expenditure", range=y_limit_range_ee, row=3, col=1)
                fig.update_xaxes(range=x_limit_range, row=1, col=1)
                fig.update_xaxes(range=x_limit_range, row=2, col=1)
                fig.update_xaxes(title_text="Activity", range=x_limit_range, row=3, col=1)
    
            elif model_name == "RMR MK":
                # TODO: Implement
                rmr = rmr_without_activity_data()
                pass
            elif model_name == "None":
                return create_empty_plot("Please select BMR/RMR model first")
            else:
                return create_empty_plot("Please update BMR/RMR model first")
    
            for x, y in spans:
                fig.add_vrect(
                    x0=x,
                    x1=y,
                    fillcolor=COLOR_NIGHTTIME,
                    line_width=0,
                    layer="below",
                    opacity=1,
                )
    
            for daychange in getIndexOf24HourInterval(energy_expenditure_all.index):
                fig.add_vline(
                    x=daychange,
                    line_width=2,
                    line_dash="dash",
                    line_color=COLOR_DATECHANGE,
                    opacity=1,
                    layer="below",
                )
            fig.update_layout(legend_title="", template="simple_white", height=900)
            fig.update_xaxes(showline=True, linewidth=1, linecolor="black", ticks="outside")
            fig.update_yaxes(showline=True, linewidth=1, linecolor="black", ticks="outside")
    
            if caliData(session).plotXlabelDay == "day":
                fig.update_xaxes(tickformat="%H:%M\nDay %_j")  ### show day 1 instead of exact date
    
            return fig
          
        except Exception as e:
            print(f"Error in rmr_plot: {e}")
            return create_empty_plot("")


    @reactive.Effect
    @reactive.event(input.rmr_prev)
    def rmr_prev():
        if caliData(session) is not None:
            index = rmr_seriesToShow()
            index -= 1
            if index < 0:
                index = (
                    caliData(session)
                    .measurementDateTimeIndexed(input.rmr_measurement_no_1())
                    .columns.size
                    - 1
                )
            rmr_seriesToShow.set(index)
            rmr_update()

    @reactive.Effect
    @reactive.event(input.rmr_next)
    def rmr_next():
        if caliData(session) is not None:
            index = rmr_seriesToShow()
            index += 1
            if (
                index
                >= caliData(session)
                .measurementDateTimeIndexed(input.rmr_measurement_no_1())
                .columns.size
            ):
                index = 0
            rmr_seriesToShow.set(index)
            rmr_update()

    def filtering(data: pd.DataFrame):
        return data.get(data.columns.tolist()[rmr_seriesToShow()])

    @output
    @render.text
    def rmr_sample():
        try: 
            curr_sample = caliData(session).measurementDateTimeIndexed(input.rmr_measurement_no_1()).columns.tolist()[rmr_seriesToShow()]
        except:
            curr_sample = ""
        return curr_sample

    @output
    @render.table
    @reactive.event(rmr_update_toggle)
    def show_rmr_bmr_table():
        if caliData(session) is not None:
            metadataTable = caliData(session).additionalData.copy()
            if model_name == "BMR/RMR":
                metadataTable2 = metadataTable[['box', 'BMR_intercept', 'beta_cca2', 'beta_tef', ]]
            elif model_name == "RMR only":
                metadataTable2 = metadataTable[['box','beta_cca1','RMR_intercept']]
            return metadataTable2

    @output
    @render.download(
        filename=lambda: f"slicedData-{datetime.datetime.now().isoformat('_', 'seconds')}.pdf"
    )
    def rmr_bmr_plot_downloader():
        fig = rmr_plot()
        if fig is None:
            return "", "application/pdf"  # Return an empty response if no figure
        try:
            imb = fig.to_image(format="pdf", width=750, height=750, scale=1)
            buf = io.BytesIO(imb)
            buf.seek(0)
            return buf.getvalue(), "application/pdf"
        except:
            pass
