import logging

import pandas as pd
import scipy

from calopy.maths.filter.Filter import Filter

UNVAR_SPLINE = "Univariate spline"


class UnivariateSpline(Filter):

    type = UNVAR_SPLINE
    logger = logging.getLogger(__name__)

    def __init__(self, smoothingfactor):
        self.smoothingfactor = smoothingfactor

    def apply(self, dataFrame: pd.DataFrame):
        print("univariateSpline with smoothingfactor: " + str(self.smoothingfactor))
        splined = {}
        for column in dataFrame:
            xVal = range(0, len(dataFrame.index))
            spl = scipy.interpolate.UnivariateSpline(
                xVal, dataFrame[column].to_list(), s=self.smoothingfactor
            )
            splined[column] = pd.Series(xVal).apply(spl)
            splined[column].index = dataFrame.index
        return pd.DataFrame(splined)

    def get_parameter_text(self):
        txt = "smoothingfactor:" + str(self.smoothingfactor)
        return txt
