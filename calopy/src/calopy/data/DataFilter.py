import logging
import string

import pandas as pd

from calopy.maths.filter.DoNothingOnFrameFilter import DoNothingOnFrameFilter
from calopy.maths.filter.DoNothingOnSeriesFilter import DoNothingOnSeriesFilter
from calopy.maths.filter.Filter import Filter
from calopy.maths.filter.RemoveOutlierFilter import RemoveOutlierFilter


class DataFilter:

    logger = logging.getLogger(__name__)

    def __init__(self, measurements):
        self.smoothing = {}
        self.outlier = {}
        for measurement in measurements:
            self.setSmoothing(measurement, DoNothingOnSeriesFilter())
            self.applyOutlierFunc(measurement, False, 0)

    def filter(self, label: string, data: pd.DataFrame):
        print(f"doSmoothing on {label}")
        removedOutliers = self.outlier[label].apply(data)
        return self.smoothing[label].apply(removedOutliers)

    def setSmoothing(self, measurement, funcClass: Filter):
        print("setSmoothing " + funcClass.type)
        self.smoothing[measurement] = funcClass

    def getSmoothing(self, measurement):
        return self.smoothing[measurement]

    def applyOutlierFunc(self, measurement, state: bool, outlierVal: float):
        print("applyOutlierFunc {}".format(state))
        if state:
            self.outlier[measurement] = RemoveOutlierFilter(outlierVal)
        else:
            self.outlier[measurement] = DoNothingOnFrameFilter()

    def getOutlier(self, measurement):
        return self.outlier[measurement]

    def addMeasurement(self, measurement):
        self.setSmoothing(measurement, DoNothingOnSeriesFilter())
        self.applyOutlierFunc(measurement, False, 0)
