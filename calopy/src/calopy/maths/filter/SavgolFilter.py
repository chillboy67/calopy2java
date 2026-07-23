import logging

from pandas import DataFrame
from scipy.signal import savgol_filter

from calopy.maths.filter.Filter import Filter

SAVGOL = "Savitzky-Golay filter"


class SavgolFilter(Filter):

    type = SAVGOL
    logger = logging.getLogger(__name__)

    def __init__(self, window: int, order: int):
        self.window = window
        self.order = order

    def apply(self, dataFrame: DataFrame):
        print("Savgol")
        filtered = {}
        for column in dataFrame:
            filtered[column] = savgol_filter(
                dataFrame[column].reset_index(drop=True),
                int(self.window),
                int(self.order),
            )

        return DataFrame(filtered, index=dataFrame.index)

    def get_parameter_text(self):
        txt = "window:" + str(self.window) + ",order:" + str(self.order)
        return txt
