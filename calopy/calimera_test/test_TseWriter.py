import io
from types import SimpleNamespace
from unittest import TestCase

from calimera.calimera_store import CONDITIONS_CONDITIONS, addCaliDataToStore, caliState
from calimera.data import CaliDataTse
from calimera.writer.TseWriter import TseWriter

from calimera_test.example_data.TseDataTest import tse_data_test


class TestTseWriter(TestCase):

    def test_writer_header(self):
        calidata: CaliDataTse = tse_data_test()
        session = SimpleNamespace(id="123")
        addCaliDataToStore(session, calidata, None)
        caliState(session)[CONDITIONS_CONDITIONS] = ["oans", "zwoa", "drei"]
        sut = TseWriter(calidata, caliState(session))
        buf = io.BytesIO()
        sut.getHeader(buf)
        sut.getAdditionalData(buf)
        sut.getMeasurementData(buf)
        sut.getCurrentSessionState(buf)
        print(buf.getvalue())
