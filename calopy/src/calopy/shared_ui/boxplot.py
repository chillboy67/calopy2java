
from itertools import combinations

import plotly.express as px
from calopy.shared_ui.plot_config import COLOR_DATECHANGE, COLOR_NIGHTTIME, \
                                         color_transparency_blending, get_color_samples



def boxPlot_Betweengroups(
    data, dependent_var, group_order, plottype, scndfactor=None, groupcolor="group"
):
    print("boxplot between groups")
    color_palette = get_color_samples(data["group"].unique())
    show_points = "all" if data.shape[0] <= 2000 else False

    if 'feature' in data.columns:
        feature_name = " - " + data['feature'].unique()[0]
    else:
        feature_name = ""

    if 'temp_condition' in data.columns and data['temp_condition'].nunique() == 1:
        phase = " - " + data['temp_condition'].unique()[0]
    elif plottype == "daynight":
        phase = ""
    else:
        phase = ""

    ylabel = dependent_var + feature_name + phase

    if plottype == "anova":
        fig = px.box(
            data,
            x=groupcolor,
            y=dependent_var,
            points=show_points,
            title="ANOVA",
            labels={
                dependent_var: ylabel
            },
            color=groupcolor,
            category_orders={"group": group_order},
            color_discrete_map=color_palette,
        )
    elif plottype == "daynight":
        fig = px.box(
            data,
            x="temp_condition",
            y=dependent_var,
            color="group",
            points=show_points,
            title="2WAY-ANOVA",
            labels={
                dependent_var: ylabel
            },
            category_orders={"group": group_order},
            color_discrete_map=color_palette,
        )
    elif plottype == "2wayanova":
        fig = px.box(
            data,
            x="group",
            y=dependent_var,
            color=scndfactor,
            points=show_points,
            title="2WAY-ANOVA",
            labels={
                dependent_var: ylabel
            },
            category_orders={"group": group_order},
            color_discrete_map=color_palette,
        )
    return fig


def boxPlot_window_statistic_text(statannot_test_results):
    bonferroni_correction_length = len(statannot_test_results)

    def format_stat_annotation_text_window(stat_result):
        curr_bin = stat_result.box1[0]
        groups = stat_result.box1[1] + " - " + stat_result.box2[1]
        out_txt = (
            "bin "
            + str(curr_bin)
            + ": "
            + groups
            + ": p-value="
            + str(stat_result.pval)
            + ": p-value_bonferroni="
            + str(min(stat_result.pval * bonferroni_correction_length, 1))
        )
        return out_txt

    test_results_sorted = [
        item
        for _, item in sorted(
            zip([x.box1[0] for x in statannot_test_results], statannot_test_results)
        )
    ]
    test_results_output_text = "\n".join(
        [format_stat_annotation_text_window(x) for x in test_results_sorted]
    )

    output_header_text = (
        "p-value annotation legend:\nns: 0.05 < p <= 1.0\n*: 0.01 < p <= 0.05\n**: 0.001 < p <= 0.01\n***: 0.0001 < p <= 0.001\n\n"
        + test_results_sorted[0].test_str
        + ":\n"
    )
    return output_header_text + test_results_output_text


def binnedWindowsBoxPlot(data, spans, x="bin", do_swarm=False):
    y_limit_range = [min(data["value"]) * 0.95, max(data["value"]) * 1.05]
    group_order = sorted(data.loc[:, "group"].unique())
    color_palette = get_color_samples(data["group"].unique())

    if do_swarm:
        fig = px.box(
            data,
            x,
            y="value",
            color="group",
            points="all",
            category_orders={"group": group_order},
            color_discrete_map=color_palette,
        )
    else:
        fig = px.box(
            data,
            x,
            y="value",
            color="group",
            category_orders={"group": group_order},
            color_discrete_map=color_palette,
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

    fig.update_yaxes(range=y_limit_range)
    return fig


def addStatsAnnotationtoWindowedBoxPlot(fig, stats, y_max):
    for index, row in stats.iterrows():
        p_value = row["p-fdr"]
        datetime = row["datetime"]

        if p_value < 0.05 and p_value > 0.01:
            annotext = "*"
        elif p_value < 0.01 and p_value > 0.001:
            annotext = "**"
        elif p_value < 0.001:
            annotext = "***"
        else:
            annotext = ""
        fig.add_annotation(
            text=annotext,
            name="p-value",
            x=datetime,
            y=y_max,
            showarrow=False,
            font=dict(size=12, color="black"),
        )

    return fig