import os
from unittest import TestCase

from calimera.data.CaliDataCsv import CaliDataCsv
from calimera.loader import LoaderCsv


class TestLoaderCsv(TestCase):

    def setUp(self):
        absolutePath = os.getcwd()
        # take substring of absolutePath until "calimera
        absolutePath = absolutePath[: absolutePath.find("calimera")]

        self.dataCsv = LoaderCsv(
            absolutePath + "calimera/calimera_test/example_data/example_dataFile.csv"
        ).loadData()

    def test_returnMeasurements(self):
        sut: CaliDataCsv = self.dataCsv
        expected = "id_2,id_3,id_4,id_1,id_9,id_10,id_11,id_12".split(",")
        self.assertEqual(expected, sut.data.columns.tolist())

    def test_selectData(self):
        sut: CaliDataCsv = self.dataCsv
        # print(sut.measurementData)
        print(sut.dataToAnalyse())
