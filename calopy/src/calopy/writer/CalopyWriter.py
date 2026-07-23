import datetime
import io

import pandas as pd

from calopy.data import CaliDataTse

STD_DATE_TIME_FORMAT = "%d/%m/%Y %H:%M"
STD_SEP = ";"
ARRAY_SEP = ","
DICT_SEP = "::"
KEY_VALUE_SEP = "="


class CalopyWriter:

    def __init__(self, caliData: CaliDataTse, caliState: dict):
        self.caliData = caliData
        self.caliState = caliState

    def getHeader(self, buf: io.BytesIO):
        # return the string of current calopy version etc todo: update this
        buf.write(b"Calopy settings:\n")
        buf.write(b"\n")

    def getAdditionalData(self, buf: io.BytesIO):
        self.caliData.additionalData.to_csv(buf, sep=";", index=False)

    def getMeasurementData(self, buf: io.BytesIO):
        measurements = self.caliData.measurementData

        header = measurements.columns.levels[1].tolist()
        header.remove("date")
        header.remove("time")
        if "box" in header:
            header.remove("box")

        # write header beginning with Date, Time, Box and the entries of headers
        buf.write(STD_SEP.join(["Date", "Time", "Box"] + header).encode())
        buf.write(b"\n")

        # units
        buf.write(STD_SEP.join(["dd/mm/yyyy", "hh:mm", "no"]).encode())
        for measurement in header:
            if self.caliData.units is not None and measurement in self.caliData.units:
                buf.write(self.caliData.units[measurement].encode())
                print(f"{measurement} is found in units.")
            else:
                print(f"Warning: {measurement} not found in units.")
            buf.write(STD_SEP.encode())
        buf.write(b"\n")

        for sample in self.caliData.samples():
            data = self.caliData.data[sample]
            # iterate over every entry in dataframe
            for index, row in data.iterrows():
                rowAsString = row.astype(str)
                # write Date, Time, Box and the entries of headers
                buf.write(index.strftime("%d/%m/%Y").encode())
                buf.write(STD_SEP.encode())
                buf.write(index.strftime("%H:%M").encode())
                buf.write(STD_SEP.encode())
                buf.write(sample.encode())
                buf.write(STD_SEP.encode())
                for measurement in header:
                    buf.write(rowAsString[measurement].encode())
                    buf.write(STD_SEP.encode())
                buf.write(b"\n")

    def getCurrentSessionState(self, buf: io.BytesIO):
        caliData = self.caliData

        # get calidata for the session and write a line per measuremnet to the buf with the fitername and the parameters seperated by sep
        self.writeLine(buf, "Preprocessing:")
        self.writeLine(buf, "Data trimming:")
        self.writeLine(
            buf,
            "croppedStart" + STD_SEP + self.caliData.croppedStart.strftime(STD_DATE_TIME_FORMAT),
        )
        self.writeLine(
            buf,
            "croppedEnd" + STD_SEP + self.caliData.croppedEnd.strftime(STD_DATE_TIME_FORMAT),
        )
        self.writeLine(buf, "night" + STD_SEP + self.caliData.night.strftime("%H:%M"))
        self.writeLine(buf, "day" + STD_SEP + self.caliData.day.strftime("%H:%M"))
        self.writeLine(buf, "Options:")
        self.writeLine(buf, "excludedSamples" + STD_SEP + ",".join(self.caliData.excludedSamples))

        self.writeLine(buf, "Filtering:")
        for measurement in self.caliData.measurements():
            filter = self.caliData.filter
            self.writeLine(
                buf,
                STD_SEP.join(
                    [
                        measurement,
                        filter.smoothing[measurement].type,
                        filter.smoothing[measurement].get_parameter_text(),
                        filter.outlier[measurement].type,
                        filter.outlier[measurement].get_parameter_text(),
                    ]
                ),
            )

        self.writeLine(buf, "Other:")
        self.writeLine(buf, "groupedBy" + STD_SEP + self.caliData.groupedBy)
        self.writeLine(buf, "calopy CaliState")
        # loop over all entries in caliState and write them to the buf as key value pairs
        for key, value in self.caliState.items():
            valueAsString = self.valueToTypeAndString(value)

            # assigne the type of value to a string variable
            # write the key, type and value to the buf
            self.writeLine(buf, STD_SEP.join([key, valueAsString]))

    def valueToTypeAndString(self, value):
        valueAsString = "None"
        # print ( f"value {type(value)}")
        if isinstance(value, bool):
            valueAsString = str(value)
        elif isinstance(value, int):
            valueAsString = str(value)
        elif isinstance(value, float):
            valueAsString = str(value)
        elif isinstance(value, pd.Timestamp) or isinstance(value, datetime.datetime):
            valueAsString = value.strftime(STD_DATE_TIME_FORMAT)
        elif isinstance(value, list):
            valueAsString = ARRAY_SEP.join(self.valueToTypeAndString(item) for item in value)
        elif isinstance(value, dict):
            valueAsString = DICT_SEP.join(
                KEY_VALUE_SEP.join([key, self.valueToTypeAndString(value)])
                for key, value in value.items()
            )
        elif value:
            valueAsString = value
        return type(value).__name__ + STD_SEP + valueAsString

    def writeLine(self, buf: io.BytesIO, line: str):
        buf.write(line.encode())
        buf.write(b"\n")

    def writeToSingleFile(self, buf):
        self.getHeader(buf)
        self.getAdditionalData(buf)
        buf.write(b"\n")
        self.getMeasurementData(buf)
        buf.write(b"\n")
        self.getCurrentSessionState(buf)

    def writeMetadataToFile(self, buf):
        self.getAdditionalData(buf)

    def writeMetabolicVarsToFile(self, buf):
        self.getMeasurementData(buf)

    def writeSettingsToFile(self, buf):
        self.getHeader(buf)
        self.getCurrentSessionState(buf)
