from unittest import TestCase

import pandas as pd
from calimera.maths.series_utils import getDefaultValueTypeSeries


class Test(TestCase):

    def test_getDefaultValueTypeSeries(self):
        series_numeric = pd.Series([10, 20, 30, 40, 50])
        series_numeric2 = pd.Series([10, 20, 30, 40, 50, "na"])
        series_numeric3 = pd.Series([10, 20, 30, 40, 50, pd.nan])
        series_numeric4 = pd.Series(["10", "20", "30", 40, 50, pd.nan])
        series_string = pd.Series(["apple", "banana", "orange", "grape", "kiwi"])
        series_string2 = pd.Series(["apple", "banana", "Nan", "grape", "kiwi", 50])
        series_string3 = pd.Series([10, 20, 30, 40, 50, "green"])
        series_date = pd.Series(pd.date_range(start="2023-07-18", periods=5))
        series_boolean = pd.Series([True, False, False, True, True])
        series_categorical = pd.Series(
            pd.Categorical(
                ["red", "blue", "green", "blue", "red"],
                categories=["red", "blue", "green"],
            )
        )
        series_categorical2 = pd.Series(["red", "blue", "NaN", "red", "kiwi", 50, "blue", "blue"])

        self.assertEqual(getDefaultValueTypeSeries(series_numeric), "numeric")
        self.assertEqual(getDefaultValueTypeSeries(series_numeric2), "numeric")
        self.assertEqual(getDefaultValueTypeSeries(series_numeric3), "numeric")
        self.assertEqual(getDefaultValueTypeSeries(series_numeric4), "numeric")
        self.assertEqual(getDefaultValueTypeSeries(series_string), "character")
        self.assertEqual(getDefaultValueTypeSeries(series_string2), "character")
        self.assertEqual(getDefaultValueTypeSeries(series_string3), "character")
        self.assertEqual(getDefaultValueTypeSeries(series_date), "NA")
        self.assertEqual(getDefaultValueTypeSeries(series_boolean), "numeric")
        self.assertEqual(getDefaultValueTypeSeries(series_categorical), "character")
        self.assertEqual(getDefaultValueTypeSeries(series_categorical2), "character")
