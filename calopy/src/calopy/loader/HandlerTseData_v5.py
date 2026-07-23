import logging
import re

import pandas as pd

from calopy.loader.handler import Handler
from calopy.loader.HandlerEof import EofHandler


class TseDataHandler_V5(Handler):
    handlerName = "TseData"
    logger = logging.getLogger(__name__)

    def __init__(self, seperator):
        self.boxes = []
        self.validateAndHandle = self.parseHeader_1
        self.header_template_1 = ["date", "time", "ref"]
        self.header_template_1_exact = self.header_template_1
        self.header_template_2 = ["", "", "s.flow"]
        self.boxes_list = []
        self.box_index = []
        self.units = {}
        self.boxes_dict = {}
        self.dataFrame: pd.DataFrame
        self.seperator = seperator

    def parsedData(self):
        dict_dataFrame = {}
        for box in self.boxes_list:
            dict_dataFrame[box] = pd.DataFrame(
                self.boxes_dict[box],
                index=self.header_template_1_exact + self.box_index,
            ).transpose()
        out_df = pd.concat(dict_dataFrame, axis=1, names=["boxes", "measurements"])

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

    def parseHeader_1(self, lineAsList):
        headerList = list(filter(lambda entry: entry, lineAsList))
        matches = 0
        if len(headerList) != 0:
            matches = 0
            for i, header_item in enumerate(headerList):

                ### check first two items for exact "date" and "time"
                if i < 2:
                    if re.fullmatch(self.header_template_1[i], header_item, re.IGNORECASE):
                        matches += 1
                    else:
                        break
                elif re.compile(rf"^{self.header_template_1[2]}", re.IGNORECASE).match(
                    header_item.lower()
                ):
                    matches += 1
                else:
                    break
            self.header_template_1_exact = headerList[0:matches]

            if matches >= len(self.header_template_1) and headerList[matches].lower().startswith(
                "box"
            ):
                self.header_template_2 = self.header_template_2[0:2] + [
                    self.header_template_2[2]
                ] * (matches - 2)
                self.validateAndHandle = self.parseHeader_2
                for box in headerList:
                    if re.search(r"^box[- ]?", box, re.IGNORECASE):
                        self.boxes.append(box[4:])
        return None

    def parseHeader_2(self, lineAsList):
        matches = 0
        offset = len(self.header_template_2)
        for i in range(offset):
            matches += lineAsList[i].lower() == self.header_template_2[i]
        if matches == offset:
            for measurement in lineAsList[offset:]:
                if measurement and not self.box_index.count(measurement) > 0:
                    self.box_index.append(measurement)
            for box in self.boxes:
                self.boxes_list.append(box)
                self.boxes_dict[box] = {}
            self.validateAndHandle = self.parseUnits
        return None

    def parseUnits(self, lineAsList):
        print(f"check for units")
        offset = len(self.header_template_1_exact)
        for entry in self.header_template_1_exact:
            self.units[entry] = ""
        for i in range(0, len(self.box_index)):
            self.units[self.box_index[i]] = lineAsList[offset + i]
        self.validateAndHandle = self.data

    def data(self, lineAsList):
        if lineAsList[0] != "":
            self.dateCache = lineAsList[0]
        else:
            lineAsList[0] = self.dateCache

        if len(lineAsList) > 1:
            offset = len(self.header_template_1_exact)
            prefix = lineAsList[:offset]
            for box in self.boxes_list:
                frame = self.boxes_dict[box]
                frame[len(frame) + 1] = prefix + lineAsList[offset : offset + len(self.box_index)]
                offset += len(self.box_index)
        else:
            return EofHandler()

        return None


class AdditionalDataHandler_V5(Handler):
    handlerName = "AdditionalData"
    logger = logging.getLogger(__name__)

    def parsedData(self):
        return self.dataFrame

    def __init__(self, seperator):
        self.validateAndHandle = self.parseHeader
        self.seperator = seperator
        self.dataFrame: pd.DataFrame = None

    def handle(self, line):
        return self.validateAndHandle(line)

    def parseHeader(self, line):
        if re.search("box", line, re.IGNORECASE) is not None:
            print("header found")
            filtered = filter(lambda it: it != "", line.split(self.seperator))
            index = map(lambda it: it.strip(), filtered)
            df_index = [
                item if isinstance(item, int) or item.lower() != "box" else "box" for item in index
            ]
            self.dataFrame = pd.DataFrame(index=df_index)
            self.validateAndHandle = self.parseData
        return None

    def parseData(self, line):
        # print("data: {}".format(line))
        lineAsList = list(filter(lambda it: it != "", line.split(self.seperator)))
        if len(lineAsList) > 0:
            self.dataFrame[self.dataFrame.columns.size + 1] = lineAsList
            return None
        else:
            self.dataFrame = self.dataFrame.transpose()
            return TseDataHandler_V5(self.seperator)
