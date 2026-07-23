import logging

import pandas as pd
import numpy as np
from CosinorPy import cosinor1

from calopy.maths.filter.Filter import Filter

SINGLE_COMPONENT_COSINOR = "Single-component cosinor"


class SingleComponentCosinorFilter(Filter):
    logger = logging.getLogger(__name__)
    type = SINGLE_COMPONENT_COSINOR

    def __init__(self, daylength: int):
        self.daylength = daylength

    def apply(self, dataFrame):
        print("single-component cosinor")
        try:
            smoothedSeries = {}
            for col in dataFrame.columns:
                series = dataFrame[col]
                datetimeIndex = series.index
                fit_results, amp, acr, statistics = cosinor1.fit_cosinor(
                    X=range(0, len(series)),
                    Y=series.reset_index(drop=True),
                    period=self.daylength,
                    plot_on=False,
                )
                series_fit = fit_results.fittedvalues
                if len(series_fit) is not len(series):
                    series_fit = self.fix_series_length(series, statistics)

                series_fit.index = datetimeIndex
                smoothedSeries[col] = series_fit
        except Exception as e:
            print("exception single-component cosinor: " + str(e))
            re = dataFrame
        frame = pd.DataFrame(smoothedSeries)
        return frame

    def get_parameter_text(self):
        txt = "daylength:" + str(self.daylength)
        return txt

    def fix_series_length(self, series_original, statistics):
        mesor = statistics["values"][0]
        amplitude = statistics["values"][1]
        phase = statistics["values"][2]
        x = np.arange(len(series_original))
        series_fitted = mesor + amplitude * np.cos((2 * np.pi * x / self.daylength) + phase)
        return pd.Series(series_fitted, index=series_original.index)
