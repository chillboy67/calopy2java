import datetime
from unittest import TestCase

from calimera.maths.filter.NightAndDayFilter import NightAndDayFilter
from example_data.TseDataTest import tse_data_test


class TestNightAndDayFilter(TestCase):
    def setUp(self):
        self.caliDataTse = tse_data_test()

    def test_apply(self):
        sut = NightAndDayFilter(
            datetime.datetime.strptime("22:00", "%H:%M").time(),
            datetime.datetime.strptime("07:00", "%H:%M").time(),
        )
        print(sut.apply(self.caliDataTse.measurementFilteredGroupedDateTimeIndexed("measurement")))
