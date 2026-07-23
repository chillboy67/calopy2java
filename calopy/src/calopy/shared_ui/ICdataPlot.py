import datetime
import io

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from scipy.stats import sem

from calopy.maths.series_utils import getAreasWhereDatetimIndexIs, getIndexOf24HourInterval
from calopy.shared_ui.plot_config import COLOR_DATECHANGE, COLOR_NIGHTTIME, \
                                         color_transparency_blending, get_color_samples


def calorimetryDataPlot(
    data,
    data_ungrouped,
    spans,
    add_feature_peaks=False,
    feature_df=None,
    add_sem=False,
    xlabel_name="date",
):

    print("IC Plot")
    color_palette = get_color_samples(data.columns)

    if xlabel_name == "day":
        ### make all files start on 1st january to show day 1 instead of exact date in plot
        days_difference = (pd.Timestamp("2018-01-01").date() - data.index[0].date()).days -1
        data.index = data.index + pd.DateOffset(days=days_difference)
        data_ungrouped.index = data_ungrouped.index + pd.DateOffset(days=days_difference)
        spans = [
            (
                start + pd.DateOffset(days=days_difference),
                end + pd.DateOffset(days=days_difference),
            )
            for start, end in spans
        ]
        if add_feature_peaks:
            if feature_df["index"][0] is not None and feature_df["feature"][0] != "raw data":
                feature_df["index"] = feature_df["index"] + pd.DateOffset(days=days_difference)

    fig = px.line(data, color_discrete_map=color_palette)

    y_limit_range = [min(data.min()) * 0.95, max(data.max()) * 1.05]
    x_limit_range = [data.index.min(), data.index.max()]

    if add_sem:
        assert isinstance(
            data_ungrouped.T.groupby(level=0)
            .agg(lambda x: sem(x, axis=None, nan_policy="omit"))
            .T,
            object,
        )
        dataframe_sem_per_group = (
            data_ungrouped.T.groupby(level=0).agg(lambda x: sem(x, axis=None, nan_policy="omit")).T
        )

        for group in data.columns:
            group_df = data[[group]]
            group_df[["lower_sem"]] = group_df[[group]] - dataframe_sem_per_group[[group]]
            group_df[["upper_sem"]] = group_df[[group]] + dataframe_sem_per_group[[group]]

            fig.add_trace(
                go.Scatter(
                    x=pd.concat([pd.Series(group_df.index), pd.Series(group_df.index[::-1])]),
                    y=pd.concat([group_df["upper_sem"], group_df["lower_sem"][::-1]]),
                    fill="toself",
                    fillcolor=color_palette[group],
                    opacity=0.3,
                    line=dict(color="rgba(255,255,255,0)"),
                    hoverinfo="skip",
                    name=group + "_SEM",
                    showlegend=True,
                )
            )

    if add_feature_peaks:
        if feature_df["index"][0] is not None and feature_df["feature"][0] != "raw data":
            fig.add_trace(
                go.Scattergl(
                    x=feature_df["index"],
                    y=feature_df["value"],
                    mode="markers",
                    marker=dict(
                        size=10,
                        symbol="circle",
                        color=feature_df["group"].map(color_palette),
                    ),
                    name=feature_df["feature"][0],
                    hovertext=feature_df["box"]
                    + " "
                    + feature_df["group"]
                    + ": "
                    + feature_df["feature"][0],
                )
            )

    for x, y in spans:
        fig.add_vrect(
            x0=x,
            x1=y,
            fillcolor=COLOR_NIGHTTIME,
            line_width=0,
            layer="below",
            opacity=1,
        )

    for daychange in getIndexOf24HourInterval(data.index):
        fig.add_vline(
            x=daychange,
            line_width=2,
            line_dash="dash",
            line_color=COLOR_DATECHANGE,
            opacity=1,
            layer="below",
        )

    fig.data = fig.data[::-1]  ### reverse plot line layer order
    fig.update_layout(
        template="simple_white",
    ),
    fig.update_yaxes(
        range=y_limit_range,
        showline=True,
        linewidth=1,
        linecolor="black",
        ticks="outside",
    )

    if xlabel_name == "day":
        fig.update_xaxes(tickformat="%H:%M\nDay %_j")  ### show day 1 instead of exact date

    return fig


def conditionsStatsPlot(GroupdDataframe, group_order, dependent_var="", dependent_feature=""):
    fig = go.Figure()

    ylabel = f"{dependent_var} - {dependent_feature}"

    error_bar_data = (
        GroupdDataframe.groupby(["condition", "group"])
        .agg({"feature": ["mean", "std"]})
        .reset_index()
    )
    color_palette = get_color_samples(GroupdDataframe["group"].unique())
    group_order = group_order[::-1]

    for group_name in group_order:
        group_data = error_bar_data[error_bar_data["group"] == group_name]
        color = color_palette[group_name]  # Use the color from the provided color palette
        fig.add_trace(
            go.Scatter(
                x=group_data["condition"],
                y=group_data[("feature", "mean")],
                mode="markers+lines",
                name=f"Group {group_name}",
                line=dict(color=color, width=2),  # Use the color from the provided color palette
                error_y=dict(
                    type="data",
                    array=group_data[("feature", "std")],
                    visible=True,
                    color=color,  # Match color of the line
                    thickness=2,
                    width=4,
                ),
            )
        )

    fig.update_layout(
        template="simple_white",
        title="",
        xaxis_title="Condition",
        yaxis_title=ylabel,
    )
    return fig



