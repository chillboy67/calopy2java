import matplotlib
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

COLOR_NIGHTTIME = "#ececec"  # light grey
COLOR_DATECHANGE = "#a6a6a6"  # dark grey


COLOR_SPANS = [   "#33cc33",  # Green
                  "#FFFF00",  # Yellow
                  "#D00000",  # Red
                  "#0000FF",  # Blue
                  "#FFA500",  # Orange
                  "#800080",  # Purple
                  "#008080"  # Teal
              ]




def get_color_samples(samples):
    color_scale = px.colors.qualitative.G10
    colors = list(color_scale)
    num_available_colors = len(colors)

    samples_sorted = sorted([str(x) for x in list(set(samples))])
    sample_color_mapping = {}
    for i, sample in enumerate(samples_sorted):
        color_index = i % num_available_colors
        color = colors[color_index]
        sample_color_mapping[sample] = color
    return sample_color_mapping


def color_transparency_blending(hex_color, alpha):
    foreground_tuple = matplotlib.colors.hex2color(hex_color)
    foreground_arr = np.array(foreground_tuple)
    final = tuple((1.0 - alpha) + foreground_arr * alpha)
    return final


def create_empty_plot(txt):
    fig = go.Figure().add_annotation(x=2, y=4, text=txt, showarrow=False)
    fig.update_layout(xaxis_visible=False, yaxis_visible=False, template="simple_white", dragmode=False)
    return fig
