import logging
import re

import pandas as pd

from calopy.loader.handler import Handler
from calopy.loader.HandlerCaliState import CaliStateHandler


class TseDataHandler_V7(Handler):
    handlerName = "TseData"
    logger = logging.getLogger(__name__)

    def __init__(self, seperator):
        self.validateAndHandle = self.parseHeader
        self.header_template = ["date", "time"]
        self.data = {}
        self.units = {}
        self.dataFrame: pd.DataFrame
        self.seperator = seperator

    def parsedData(self):
        dataFrame = pd.DataFrame(self.data)
        boxes = set(dataFrame["box"])
        dict_of_boxes = {}
        for box in boxes:
            dict_of_boxes[box] = dataFrame[dataFrame["box"] == box]
            dict_of_boxes[box].index = range(len(dict_of_boxes[box].index))
            dict_of_boxes[box] = dict_of_boxes[box].drop(columns=["box"])
        out_df = pd.concat(dict_of_boxes, axis=1, names=["boxes", "measurements"])

        ### set date and time to lower case for calidata
        out_df.columns = pd.MultiIndex.from_tuples(
            [
                (
                    boxes,
                    (
                        measurements.lower()
                        if measurements.lower() in ["date", "time"]
                        else measurements
                    ),
                )
                for boxes, measurements in out_df.columns
            ]
        )

        ### add units to measurements
        out_df.columns = pd.MultiIndex.from_tuples(
            [
                (
                    boxes,
                    (
                        f"{measurements} {self.units[measurements]}"
                        if measurements in self.units and self.units[measurements]
                        else measurements
                    ),
                )
                for boxes, measurements in out_df.columns
            ]
        )

        return out_df

    def handle(self, line):
        return self.validateAndHandle(line.split(self.seperator))

    def parseHeader(self, lineAsList):
        print(f"check for header with {self.seperator.join(self.header_template)}")
        headerList = lineAsList
        matches = 0
        for i in range(len(self.header_template)):
            matches += headerList[i].lower() == self.header_template[i].lower()
        if matches == len(self.header_template):
            self.validateAndHandle = self.parseUnits
            for index in headerList:
                index = index.lower() if "box" in index.lower() else index
                self.data[index] = []
        return None

    def parseUnits(self, lineAsList):
        print(f"check for units")
        self.validateAndHandle = self.parseData
        keys = list(self.data.keys())
        for i in range(len(keys)):
            self.units[keys[i]] = lineAsList[i]
        return None

    def parseData(self, lineAsList):
        # print(F"data: {self.seperator.join(lineAsList)}")
        keys = list(self.data.keys())
        # dataFrame.columns = [col.lower() if "box" in col.lower() else col for col in dataFrame.columns]
        if len(lineAsList) < len(keys):
            return CaliStateHandler(self.seperator)
        for i in range(len(keys)):
            self.data[keys[i]].append(lineAsList[i])
        return None


class AdditionalDataHandler_V7(Handler):
    handlerName = "AdditionalData"
    logger = logging.getLogger(__name__)

    def parsedData(self):
        dataFrame = self.dataFrame
        dataFrame.columns = [
            col.lower() if "box" in col.lower() else col for col in dataFrame.columns
        ]
        return dataFrame

    def __init__(self, seperator):
        self.validateAndHandle = self.header
        self.dataFrame: pd.DataFrame = None
        self.seperator = seperator

    def handle(self, line):
        return self.validateAndHandle(line)

    def header(self, line):
        if re.search("box", line.lower()) is not None:
            print("header found")
            split = line.split(self.seperator)
            filtered = filter(lambda it: it != "", split)
            index = list(map(lambda it: it.strip(), filtered))
            df_index = [
                item if isinstance(item, int) or item.lower() != "box" else "box" for item in index
            ]
            self.dataFrame = pd.DataFrame(index=index)
            self.validateAndHandle = self.data
        return None

    def data(self, line):
        # print("data: {}".format(line))
        lineAsList = list(filter(lambda it: it != "", line.split(self.seperator)))
        if len(lineAsList) > 0:
            self.dataFrame[self.dataFrame.columns.size + 1] = lineAsList
            return None
        else:
            self.dataFrame = self.dataFrame.transpose()
            return TseDataHandler_V7(self.seperator)
