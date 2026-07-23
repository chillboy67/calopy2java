import logging

from calopy.maths.filter.Filter import Filter

ROLLING_WINDOW_GAUSIAN = "Rolling window - Gaussian"


class RollingWindowGausianFilter(Filter):
    logger = logging.getLogger(__name__)
    type = ROLLING_WINDOW_GAUSIAN

    def __init__(self, window: int, deviation: int):
        self.window = window
        self.deviation = deviation

    def apply(self, series):
        print("rollingWindowGausian")
        return series.rolling(
            window=int(self.window), win_type="gaussian", center=True, min_periods=1
        ).mean(std=int(self.deviation))

    def get_parameter_text(self):
        txt = "window:" + str(self.window) + ",deviation:" + str(self.deviation)
        return txt
