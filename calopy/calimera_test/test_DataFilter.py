import unittest
from unittest import TestCase

from calimera.data import DataFilter
from calimera.maths.filter.RollingWindowMeanFilter import RollingWindowMeanFilter

from calimera_test.example_data.TseDataTest import MEASUREMENT, tse_data_test


class TestDataFilter(TestCase):

    def setUp(self):
        self.caliDataTse = tse_data_test()

    def test_removeOutliers(self):
        sut: DataFilter = DataFilter.DataFilter([MEASUREMENT])
        sut.applyOutlierFunc(MEASUREMENT, True, 2.0)
        print(
            sut.filter(
                MEASUREMENT,
                self.caliDataTse.measurementFilteredGroupedDateTimeIndexed(MEASUREMENT),
            )
        )

    def test_applySmooting(self):
        sut: DataFilter = DataFilter.DataFilter([MEASUREMENT])
        sut.setSmoothing(MEASUREMENT, RollingWindowMeanFilter(10))
        print(self.caliDataTse.measurementFilteredGroupedDateTimeIndexed(MEASUREMENT))
        print(
            sut.filter(
                MEASUREMENT,
                self.caliDataTse.measurementFilteredGroupedDateTimeIndexed(MEASUREMENT),
            )
        )

    def test_applyGrouping(self):
        sut: DataFilter = DataFilter.DataFilter([MEASUREMENT])
        group = self.caliDataTse.getCategoricalColumns()[1]
        result = self.caliDataTse.doGrouping(self.caliDataTse.data, group)
        print(result)


if __name__ == "__main__":
    unittest.main()
