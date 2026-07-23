import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt

from calopy.maths import statistic
from calopy.shared_ui.plot_config import get_color_samples


def createScatterplotFigure(data_one, data_two, data_one_title, data_two_title, doRegAnnotations=False):
    print("createScatterplotFigure")
    fig, ax = plt.subplots()
    ax.set_ylabel(data_one_title)
    ax.set_xlabel(data_two_title)
    regression_results = {}

    # Get color samples based on unique column names in both dataframes
    unique_columns = data_two.columns.union(data_one.columns)[::-1]
    color_palette = get_color_samples(unique_columns)
    default_color = "teal"
    formatted_results = ""

    # Iterate over each column in data_one and corresponding column in data_two
    for label in unique_columns:
        if label in data_one and label in data_two:
            data1_series = data_one[label].dropna()
            data2_series = data_two[label].dropna()

            common_index = data1_series.index.intersection(data2_series.index)
            data1_series = data1_series.loc[common_index]
            data2_series = data2_series.loc[common_index]

            plot_color = color_palette.get(label, default_color)

            ax.scatter(
                data1_series,
                data2_series,
                label=f"{label}",
                alpha=0.7,
                color=plot_color,
            )

            if doRegAnnotations and not data1_series.empty and not data2_series.empty:
                slope, intercept, r_value, p_value, std_err = statistic.linear_regression(
                    data1_series, data2_series
                )
                ax.plot(
                    data1_series,
                    intercept + slope * data1_series,
                    label=f"Regression {label}",
                    color=plot_color,
                )
                regression_results[label] = {
                    "slope": slope,
                    "intercept": intercept,
                    "r_value": r_value,
                    "p_value": p_value,
                    "std_err": std_err,
                }
                formatted_results += f"{label} Regression:\nSlope: {slope:.5f}\nIntercept: {intercept:.5f}\nR-squared: {r_value ** 2:.5f}\nP-value: {p_value:.5f}\nStandard Error: {std_err:.5f}\n\n"

    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    return fig, formatted_results if doRegAnnotations else ""


def createScatterplotFigure_new(data_one, data_two, data_one_title, data_two_title, doRegAnnotations=False):
    print("createScatterplotFigure")

    data_one = data_one.iloc[:, 0]
    data_two = data_two.iloc[:, 0]
    print(data_one)
    print(data_two)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_ylabel(data_one_title)
    ax.set_xlabel(data_two_title)

    if doRegAnnotations:
        scatterAndInterpolate(ax, data_one, data_two, color="teal")
        formatted_results = reganalysis(data_one, data_two)
        return formatted_results

    scatterAndInterpolate(ax, data_one, data_two, color="teal")
    return fig


def scatterAndInterpolate(ax, data_one, data_two, color):
    key_first_column = "one"
    key_second_column = "two"
    data_one.name = key_first_column
    data_two.name = key_second_column
    concat = pd.concat([data_one, data_two], axis=1).sort_values(key_first_column, axis=0)
    ax.scatter(concat[key_first_column], concat[key_second_column], marker=".", c=color)
    try:
        slope, intercept, r_value, p_value, std_err = statistic.linear_regression(
            concat[key_first_column].dropna(), concat[key_second_column].dropna()
        )
        print(slope, intercept)
        ax.plot(
            concat[key_first_column],
            intercept + slope * concat[key_first_column],
            "-",
            color=color,
        )
    except Exception as e:
        print(e)


def reganalysis(data_one, data_two):
    key_first_column = "one"
    key_second_column = "two"
    regression_results = {}
    formatted_results = ""
    data_one.name = key_first_column
    data_two.name = key_second_column
    concat = pd.concat([data_one, data_two], axis=1).sort_values(key_first_column, axis=0)
    try:
        slope, intercept, r_value, p_value, std_err = statistic.linear_regression(
            concat[key_first_column].dropna(), concat[key_second_column].dropna()
        )
        regression_results = {
            "slope": slope,
            "intercept": intercept,
            "r_value": r_value,
            "p_value": p_value,
            "std_err": std_err,
        }
        formatted_results += f" Regression:\nSlope: {slope:.5f}\nIntercept: {intercept:.5f}\nR-squared: {r_value ** 2:.5f}\nP-value: {p_value:.5f}\nStandard Error: {std_err:.5f}\n\n"
        return formatted_results

    except Exception as e:
        print(e)


def between_groups_regression_plot(
        data, predictive_var_name, predicitve_var, dependent_var_name, dependent_var, grouping=None
):
    data.rename(columns={'temp_condition_y': 'temp_condition'}, inplace=True)
    if 'temp_condition' in data.columns:
        temp_label = f" - {data['temp_condition'][0]}"
    else:
        temp_label = f""

    if data['feature_x'][0] == predictive_var_name:
        xlabel = f"{predictive_var_name}"
    else:
        xlabel = f"{predictive_var_name} - {data['feature_x'][0]} {temp_label}"

    if data['feature_y'][0] == dependent_var_name:
        ylabel = f"{dependent_var_name}"
    else:
        ylabel = f"{dependent_var_name} - {data['feature_y'][0]} {temp_label}"

    if grouping is not None:
        plottitle = "ANCOVA"
        color_args = {
            "color": grouping,
            "color_discrete_map": get_color_samples(data[grouping].unique())
        }

    else:
        plottitle = "Linear Regression"
        grouping = "box"
        color_args = {
            "color": grouping,
            "color_discrete_map": get_color_samples(data[grouping].unique()),
            "trendline_scope": "overall",
            "trendline_color_override": "black"
        }

    fig = px.scatter(
        data,
        x=predictive_var_name,
        y=dependent_var,
        trendline="ols",
        labels={
            predictive_var_name: xlabel,
            dependent_var: ylabel,
            "group_x": grouping,
        },
        title = plottitle,
        **color_args
    )
    return fig
