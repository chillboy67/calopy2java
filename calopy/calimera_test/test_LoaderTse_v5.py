import os
from unittest import TestCase

from calimera.data.CaliDataTse import CaliDataTse
from calimera.loader.HandlerTseData_v5 import AdditionalDataHandler_V5, TseDataHandler_V5
from calimera.loader.LoaderTse import LoaderTse, TseIdentifierHandler


class TestLoaderTse_v5(TestCase):

    def test_accessFile(self):
        absolutePath = os.getcwd()
        # take substring of absolutePath until "calimera
        absolutePath = absolutePath[: absolutePath.find("calimera")]
        sut = LoaderTse(absolutePath + "calimera/test/example_data/example_tse.tsv")
        tsedata = sut.loadData()
        assert isinstance(tsedata, CaliDataTse)
        assert tsedata.additionalData is not None
        assert tsedata.data is not None

    def test_TseIdentiefier(self):
        sut = TseIdentifierHandler()
        assert sut.handle("SomethingTotallydifferent") is None
        assert isinstance(
            sut.handle("TSE PhenoMaster V5.5.8 (2015-4474)"), AdditionalDataHandler_V5
        )

    def test_AdditionalDataHandler(self):
        sut = AdditionalDataHandler_V5(";")
        assert sut.parseHeader == sut.validateAndHandle
        sut.handle("Box;Animal No.;weight_week0[g];weightGain[per];WeightGainLog;genotype;diet")
        assert sut.parseData == sut.validateAndHandle
        sut.handle("1;1;29.7;54.2;0.625;C57Bl6j;chow")
        print(sut.parsedData())
        assert 1 == sut.dataFrame.columns.size
        assert isinstance(sut.handle("whatever;;"), TseDataHandler_V5)

    def test_TseDataHandle(self):
        sut = TseDataHandler_V5(";")
        assert sut.parseHeader_1 == sut.validateAndHandle
        sut.handle("Date;Time;Ref-1.1;Ref-1.2;Box-1;;;;;;;;;;Box-11;;;;;;;;;;Box-13;;;;;;;;;;")
        expected = ["1", "11", "13"]
        assert expected == sut.boxes
        assert sut.parseHeader_2 == sut.validateAndHandle
        sut.handle(
            ";;S.Flow;S.Flow;XT+YT;XT;VO2(3);VCO2(3);Temp;RER;H(3);Flow;Feed1;Drink;XT+YT;XT;VO2(3);VCO2(3);Temp;RER;H(3);Flow;Feed1;Drink;XT+YT;XT;VO2(3);VCO2(3);Temp;RER;H(3);Flow;Feed1;Drink"
        )
        print(sut.boxes_dict)
        assert sut.parseUnits == sut.validateAndHandle
        sut.handle(
            "Stop;;[l/min];[l/min];[Cnts];[Cnts];[ml/h];[ml/h];[C];;[kcal/h];[l/min];[g];[ml];[Cnts];[Cnts];[ml/h];[ml/h];[C];;[kcal/h];[l/min];[g];[ml];[Cnts];[Cnts];[ml/h];[ml/h];[C];;[kcal/h];[l/min];[g];[ml]"
        )
        assert sut.data == sut.validateAndHandle
        sut.handle(
            "14.03.2017;14:36;0.4;0.4;0;0;64;58;22.8;0.908;0.314;0.45;0;0;177;124;60;54;21.8;0.891;0.296;0.45;0;0;38;38;76;61;21.1;0.798;0.368;0.45;0;0"
        )
        sut.handle(
            ";14:46;0.4;0.4;3;3;65;60;22.8;0.92;0.322;0.45;0;0;25;20;56;50;21.8;0.878;0.277;0.45;0;0;18;15;72;57;21;0.786;0.348;0.47;0;0"
        )
        sut.handle(
            "15.03.2017;14:56;0.4;0.4;0;0;65;60;22.8;0.922;0.322;0.46;0;0;79;46;62;55;22.1;0.882;0.306;0.45;0;0.06;18;18;72;57;21.1;0.796;0.348;0.44;0;0"
        )
        sut.handle("\n")
        print(sut.parsedData())
        print(sut.units)
