import datetime
from unittest import TestCase

from calimera.data import CaliDataTse
from calimera.maths.features import FEATURE_FUNC_DICT, MEAN
from pandas import DataFrame, Series

from calimera_test.example_data.TseDataTest import MEASUREMENT, MEASUREMENT_2, tse_data_test


class TestCaliDataTse(TestCase):
    def test_index_by_date(self):
        sut: CaliDataTse = tse_data_test()

    def test_shift_to_date(self):
        sut: CaliDataTse = tse_data_test()
        print(sut.shiftToDate(datetime.datetime.now()))

    def test_indexed_by_date(self):
        sut: CaliDataTse = tse_data_test()
        print(sut.indexByDate(sut.measurementData))

    def test_createScatterPlotFigure(self):
        sut: CaliDataTse = tse_data_test()
        sut.setGrouping("group")
        print(sut.getContinuousColumns())
        data_one = FEATURE_FUNC_DICT[MEAN](sut.measurementFilteredDateTimeIndexed(MEASUREMENT))
        sut.doGroupingByIndex(data_one, "group")

    def isNightClosure(self, nightStart, nightEnd):
        def isNight(x):
            return not nightStart > x.time() > nightEnd

        return isNight
