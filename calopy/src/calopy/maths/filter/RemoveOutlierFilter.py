import logging

import numpy as np
import pandas as pd

from calopy.maths.filter.Filter import Filter

logger = logging.getLogger(__name__)


# helper method
# detect outlier times*standard deviation and handle like NaN


def popOutliers(ser_mean, ser_std, outlierVal: float):
    def fun(x):
        if x < ser_mean - outlierVal * ser_std:
            logger.debug("Outlier found")
            return np.NaN
        if x > ser_mean + outlierVal * ser_std:
            logger.debug("Outlier found")
            return np.NaN
        return x

    return fun


REMOVE_OUTLIER = "removeOutliers"


class RemoveOutlierFilter(Filter):
    type = REMOVE_OUTLIER

    def __init__(self, outlierVal):
        self.outlierVal = outlierVal

    def apply(self, dataFrame: pd.DataFrame):
        logger.debug("RemoveOutlierFilter")
        removedOutliers = {}
        for col in dataFrame.columns:
            ser_mean = np.nanmean(dataFrame[col])
            ser_std = np.nanstd(dataFrame[col])
            popOutlier = popOutliers(ser_mean, ser_std, self.outlierVal)
            removedOutliers[col] = dataFrame[col].apply(popOutlier).interpolate(method="linear")

        return pd.DataFrame(removedOutliers)

    def get_parameter_text(self):
        txt = "stdev:" + str(self.outlierVal)
        return txt
