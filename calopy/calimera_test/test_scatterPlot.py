import functools
from unittest import TestCase

from calimera.data import CaliDataTse
from calimera.maths.features import FEATURE_FUNC_DICT, MEAN
from calimera.scatter.scatter_controller import groupedByDate

from calimera_test.example_data.TseDataTest import MEASUREMENT, MEASUREMENT_2, tse_data_test


class TestScatterPlot(TestCase):

    def test_groupedByDate(self):
        caliData: CaliDataTse = tse_data_test()
        # get the first entry of the index of caliData
        start = caliData.data.index[0]
        feature_df = groupedByDate(
            caliData.measurementFilteredDateTimeIndexed(MEASUREMENT), start
        ).agg(FEATURE_FUNC_DICT[MEAN])
        print(feature_df)

    def test_index_of_days(self):
        caliData: CaliDataTse = tse_data_test()
        data = caliData.measurementFilteredDateTimeIndexed(MEASUREMENT)
        scatter_start = data.index[0]

        print(data.index.tolist())
        dict_of_days = {x: (x - scatter_start).days for x in data.index.tolist()}
        print(f"dictionnary of days: {dict_of_days}")
        # get first entry of the values in the dictinory of days
        index_of_day_change = [list(dict_of_days.keys())[0]]

        for key in dict_of_days.keys():
            if dict_of_days[key] != dict_of_days[index_of_day_change[-1]]:
                index_of_day_change.append(key)

        print(f"index_of_day_change: {index_of_day_change}")
