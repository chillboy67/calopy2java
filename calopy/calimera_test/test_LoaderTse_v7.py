import os
from unittest import TestCase

from calimera.data.CaliDataTse import CaliDataTse
from calimera.loader.HandlerTseData_v7 import AdditionalDataHandler_V7, TseDataHandler_V7
from calimera.loader.LoaderTse import LoaderTse, TseIdentifierHandler


class TestLoaderTse_v7(TestCase):

    def test_accessFile(self):
        absolutePath = os.getcwd()
        # take substring of absolutePath until "calimera
        absolutePath = absolutePath[: absolutePath.find("calimera")]
        sut = LoaderTse(
            absolutePath + "calimera_shiny/calimera_test/example_data/example_tse_v7.tsv"
        )
        tsedata = sut.loadData()
        assert isinstance(tsedata, CaliDataTse)
        assert tsedata.additionalData is not None
        assert tsedata.data is not None

    def test_TseIdentifier(self):
        sut = TseIdentifierHandler()
        assert sut.handle("SomethingTotallydifferent") is None
        assert isinstance(
            sut.handle("TSE PhenoMaster V7.28 (2015-4474)"), AdditionalDataHandler_V7
        )

    def test_AdditionalDataHandler(self):
        sut = AdditionalDataHandler_V7(",")
        assert sut.header == sut.validateAndHandle
        sut.handle(
            "Box,Animal No.,Weight [g],Text1,Text2,Text3,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        assert sut.data == sut.validateAndHandle
        sut.handle("1,6749,21.2,F,E64-F6749,21.92,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
        print(sut.parsedData())
        assert 1 == sut.dataFrame.columns.size

    def test_TseDataHandle(self):
        sut = TseDataHandler_V7(",")
        sut.handle(
            "Date,Time,Animal No.,Box,TempC,HumC,LightC,S.Flow,Ref.O2,Ref.CO2,Flow,Temp,O2,CO2,dO2,dCO2,VO2(1),VO2(2),VO2(3),VCO2(1),VCO2(2),VCO2(3),RER,H(1),H(2),H(3),XT+YT,XT,XA,XF,YT,YA,YF,Z,CenT,CenA,CenF,PerT,PerA,PerF,DistK,DistD,Speed,Drink,Feed1"
        )
        sut.handle(
            ",,,,[�C],[%],[%],[l/min],[%],[%],[l/min],[�C],[%],[%],[%],[%],[ml/h/kg],[ml/h/kg],[ml/h],[ml/h/kg],[ml/h/kg],[ml/h],,[kcal/h/kg],[kcal/h/kg],[kcal/h],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[Cnts],[cm],[cm],[cm/s],[ml],[g]"
        )
        sut.handle(
            "06/11/2020,10:25,6749,1,23.3,54,49,0.35,20.79,0.044,0.35,22.7,20.43,0.347,0.359,0.302,3702,1413,78,2991,1141,63,0.808,17.898,6.829,0.379,2976,1552,1257,295,1424,1086,338,396,1099,933,166,1877,1410,467,2104,2104,2,0.05,0.01"
        )
        sut.handle(
            "06/11/2020,10:40,6749,1,22.9,54,49,0.35,20.8,0.046,0.35,23,20.36,0.431,0.441,0.385,4501,1718,95,3804,1451,81,0.845,21.946,8.374,0.465,3129,1708,1393,315,1421,1096,325,459,1255,1071,184,1874,1418,456,4463,2359,3,0.05,0.01"
        )
        sut.handle(
            "06/11/2020,10:55,6749,1,23.1,55,49,0.35,20.81,0.045,0.35,23.1,20.33,0.469,0.475,0.424,4843,1848,103,4197,1601,89,0.867,23.728,9.054,0.503,2790,1441,1132,309,1349,1055,294,365,1220,971,249,1570,1216,354,6516,2053,2,0.05,0.65"
        )
        sut.handle(
            "06/11/2020,11:10,6749,1,23.1,55,49,0.35,20.81,0.044,0.35,23.3,20.34,0.457,0.467,0.412,4770,1820,101,4086,1559,87,0.857,23.317,8.897,0.494,1413,810,573,237,603,401,202,107,820,533,287,593,441,152,7396,880,1,0.08,0.65"
        )
        sut.handle(
            "06/11/2020,11:25,6749,1,22.9,55,49,0.35,20.81,0.044,0.35,23.3,20.34,0.456,0.47,0.412,4799,1831,102,4076,1555,86,0.849,23.421,8.937,0.497,1621,854,641,213,767,547,220,227,617,443,174,1004,745,259,8542,1146,1,0.09,0.65"
        )
        sut.handle(
            "06/11/2020,11:40,6749,1,23.1,55,49,0.35,20.81,0.043,0.35,23.3,20.36,0.425,0.45,0.382,4624,1764,98,3775,1440,80,0.816,22.396,8.546,0.475,128,71,14,57,57,15,42,0,28,14,14,100,15,85,8601,59,0,0.09,0.65"
        )
        sut.handle(
            "06/11/2020,11:55,6749,1,23,55,49,0.35,20.81,0.043,0.35,23.4,20.44,0.345,0.373,0.302,3881,1481,82,2986,1139,63,0.769,18.597,7.096,0.394,98,68,20,48,30,7,23,0,38,13,25,60,14,46,8626,25,0,0.09,0.65"
        )
        sut.handle(
            "06/11/2020,12:10,6749,1,23.1,55,49,0.35,20.81,0.043,0.35,23.4,20.45,0.333,0.364,0.29,3804,1452,81,2879,1099,61,0.757,18.176,6.936,0.385,40,31,10,21,9,3,6,0,17,6,11,23,7,16,8637,12,0,0.1,0.65"
        )
        sut.handle(
            "06/11/2020,12:25,6749,1,23,54,49,0.35,20.81,0.043,0.35,23.4,20.48,0.308,0.336,0.265,3503,1337,74,2622,1000,56,0.749,16.704,6.374,0.354,87,53,19,34,34,5,29,0,44,11,33,43,13,30,8668,31,0,0.1,0.65"
        )
        sut.handle(
            "06/11/2020,12:40,6749,1,22.9,55,49,0.35,20.82,0.043,0.35,23.4,20.47,0.318,0.34,0.275,3529,1346,75,2719,1037,58,0.77,16.914,6.454,0.359,2357,1374,1070,304,983,732,251,365,770,608,162,1587,1194,393,10416,1747,2,0.1,0.65"
        )
        sut.handle(
            "06/11/2020,12:55,6749,1,23.1,55,49,0.35,20.81,0.043,0.35,23.4,20.39,0.393,0.42,0.35,4348,1659,92,3473,1325,74,0.799,20.976,8.004,0.445,480,295,178,117,185,77,108,3,328,159,169,152,96,56,10631,215,0,0.1,0.65"
        )
        sut.handle(
            "06/11/2020,13:10,6749,1,23,55,49,0.35,20.81,0.042,0.35,23.5,20.45,0.345,0.362,0.302,3742,1428,79,2990,1141,63,0.799,18.053,6.888,0.383,100,46,19,27,54,8,46,0,83,23,60,17,4,13,10658,28,0,0.1,0.65"
        )
        sut.handle(
            "06/11/2020,13:25,6749,1,22.9,55,49,0.35,20.81,0.042,0.35,23.4,20.48,0.31,0.331,0.268,3435,1311,73,2648,1010,56,0.771,16.465,6.283,0.349,36,21,11,10,15,1,14,0,36,12,24,0,0,0,10674,16,0,0.11,0.65"
        )
        sut.handle("\n")
        print(sut.parsedData())
        print(sut.units)
