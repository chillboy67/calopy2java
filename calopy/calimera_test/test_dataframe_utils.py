import unittest
from unittest import TestCase

import pandas as pd
from calimera.maths.dataframe_utils import convertDataFrameToSeries


class TestDataFrameUtils(TestCase):

    def test_convaert_data_frame_to_searies(self):
        array_1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        array_2 = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        array_3 = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

        dict_1 = {"A": array_1, "B": array_2, "C": array_3}
        dict_2 = {"A": array_2, "B": array_1, "C": array_3}

        df1 = pd.DataFrame(data=dict_1)
        df2 = pd.DataFrame(data=dict_2)

        result = convertDataFrameToSeries(df1, df2, "one", "two")
        print(result)


if __name__ == "__main__":
    unittest.main()
