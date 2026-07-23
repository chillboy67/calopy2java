from calopy.shared_ui.plot_config import COLOR_SPANS


def displaySpan(axes, spans):
    index = 0
    for x, y in spans:
        axes.axvspan(x, y, alpha=0.2, facecolor=COLOR_SPANS[index % len(COLOR_SPANS)])
        index += 1


def displaySpansWidget(fig, spans):
    index = 0
    for x, y in spans:
        fig.add_vrect(
            x0=x,
            x1=y,
            fillcolor=COLOR_SPANS[index % len(COLOR_SPANS)],
            line_width=0,
            layer="below",
            opacity=0.2,
        )
        index += 1
