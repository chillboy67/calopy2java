import logging

from calopy.maths.filter.Filter import Filter

ROLLING_WINDOW = "Rolling window - mean"


class RollingWindowMeanFilter(Filter):
    logger = logging.getLogger(__name__)
    type = ROLLING_WINDOW

    def __init__(self, window: int):
        self.window = window

    def apply(self, series):
        print("rollingWindowMean")
        return series.rolling(window=int(self.window), center=True, min_periods=1).mean()

    def get_parameter_text(self):
        txt = "window:" + str(self.window)
        return txt
