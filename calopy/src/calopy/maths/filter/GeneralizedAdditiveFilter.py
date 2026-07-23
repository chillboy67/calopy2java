import logging

import pandas as pd
from pygam import GAM

from calopy.maths.filter.Filter import Filter

GENERALIZED_ADDITIVE = "Generalized additive model"


class GeneralizedAdditiveFilter(Filter):
    logger = logging.getLogger(__name__)
    type = GENERALIZED_ADDITIVE

    def apply(self, dataFrame):
        print("generalizedAdditiveModel")
        try:
            smoothedSeries = {}
            for col in dataFrame.columns:
                series = dataFrame[col].dropna()
                datetimeIndex = series.index
                xVal = pd.Series(list(range(0, len(series))))
                gam = GAM().fit(xVal, series)
                smoothedSeries[col] = pd.Series(gam.predict(xVal), datetimeIndex)

        except Exception as e:
            print("exception applySmoothing_smooth_GAM: " + str(e))
            re = dataFrame
        frame = pd.DataFrame(smoothedSeries)
        return frame

    def get_parameter_text(self):
        return ""
