import logging

from calopy.maths.filter.Filter import Filter

ROLLING_WINDOW_TRIANGULAR = "Rolling window - triangular"


class RollingWindowTriangularFilter(Filter):
    logger = logging.getLogger(__name__)
    type = ROLLING_WINDOW_TRIANGULAR

    def __init__(self, window: int):
        self.window = window

    def apply(self, series):
        print("rollingWindowTriangular")
        return series.rolling(
            window=int(self.window), win_type="triang", center=True, min_periods=1
        ).mean()

    def get_parameter_text(self):
        txt = "window:" + str(self.window)
        return txt
