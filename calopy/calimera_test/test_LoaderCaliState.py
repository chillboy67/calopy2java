from types import SimpleNamespace
from unittest import TestCase

from calimera.calimera_store import addCaliDataToStore, caliState
from calimera.data import CaliDataTse
from calimera.loader.HandlerCaliState import CaliStateHandler

from calimera_test.example_data.TseDataTest import tse_data_test


class TestLoaderCaliState(TestCase):

    def test_loadCaliState(self):
        sut = CaliStateHandler(";")
        sut.handle("CALIMERA TseState")
        assert sut.validateAndHandle == sut.parseTseState
        sut.handle("Filter:")
        sut.handle("Ref-1.1;Do nothing;;Do nothing;")
        sut.handle("Ref-1.2;Do nothing;;removeOutliers;stdev:3")
        sut.handle("drink;Do nothing;;Do nothing;")
        sut.handle("drink_cumulative;Do nothing;;Do nothing;")
        sut.handle("feed1;Do nothing;;Do nothing;")
        sut.handle("feed1_cumulative;Do nothing;;Do nothing;")
        sut.handle("flow;Do nothing;;Do nothing;")
        sut.handle("h(3);Generalized additive model;;Do nothing;")
        sut.handle("rer;Rolling window - triangular;window:5;Do nothing;")
        sut.handle("temp;Do nothing;;Do nothing;")
        sut.handle("vco2(3);Savitzky-Golay filter;window:5,order:2;Do nothing;")
        sut.handle("vo2(3);Do nothing;;Do nothing;")
        sut.handle("xt;Do nothing;;Do nothing;")
        sut.handle("xt+yt;Do nothing;;Do nothing;")
        sut.handle("Other:")
        sut.handle("excludedSamples;11,13")
        sut.handle("croppedStart;14/03/2017,14:36")
        sut.handle("croppedEnd;16/03/2017,00:26")
        sut.handle("night;22:00")
        sut.handle("day;07:00")
        sut.handle("excludedSamples;")
        sut.handle("groupedBy;box")
        sut.handle("CALIMERA CaliState")
        sut.handle("scatter_grouped;str;genotype")
        sut.handle("scatter_measurement_no_1;str;vco2(3)")
        sut.handle("scatter_measurement_no_2;str;h(3)")
        sut.handle("scatter_daysplit;bool;True")
        sut.handle("scatter_start;datetime;14/03/2017 14:36")
        sut.handle("scatter_feature;str;mean")
        sut.handle(
            "conditions;list;dict;text=str;Condition:from=Timestamp;14/03/2017 14:36:to=Timestamp;17/03/2017 15:26"
        )
        for key in sut.tseFilter:
            print("key: {} value: {}".format(key, sut.tseFilter[key]))
        for key in sut.tseState:
            print("key: {} value: {}".format(key, sut.tseState[key]))
        for key in sut.caliState:
            print("key: {} value: {}".format(key, sut.caliState[key]))
        calidata: CaliDataTse = tse_data_test()
        state = sut.parsedData()
        session = SimpleNamespace(id="123")
        addCaliDataToStore(session, calidata, state)
