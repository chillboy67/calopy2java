import logging
import os
import re
import string

from calopy.data.CaliDataTse import CaliDataTse
from calopy.loader.handler import Handler
from calopy.loader.HandlerEof import EofHandler
from calopy.loader.HandlerTseData_v5 import AdditionalDataHandler_V5
from calopy.loader.HandlerTseData_v7 import AdditionalDataHandler_V7


class TseIdentifierHandler(Handler):
    handlerName = "TseIdentifier"

    def parsedData(self):
        pass

    def handle(self, line):
        return self.validate(line)

    def detect_separator(self, line):
        separators = {
            ";": line.count(";"),
            ",": line.count(","),
            "\t": line.count("\t"),
        }
        separator = max(separators, key=separators.get)
        return separator

    def validate(self, line):
        if re.search(r"TSE (PhenoMaster|LabMaster)", line) is not None:
            seperator = self.detect_separator(line)
            if re.search("v5", line.lower()):
                return AdditionalDataHandler_V5(seperator)
            if re.search("v6.2", line.lower()):
                return AdditionalDataHandler_V5(seperator)
            if re.search("v6.3", line.lower()):
                return AdditionalDataHandler_V7(seperator)
            if re.search("v7", line.lower()):
                return AdditionalDataHandler_V7(seperator)
            else:
                return AdditionalDataHandler_V7(seperator)
        return None


class LoaderTse:
    filename: string
    logger = logging.getLogger(__name__)

    def __init__(self, fileName):
        self.dataFromHandler = {}
        self.filename = fileName
        print("load file {} on {}".format(fileName, os.getcwd()))
        self.fileStream = open(fileName)

    def __del__(self):
        self.closeFile()

    def closeFile(self):
        self.fileStream.close()

    def loadData(self):
        print("loadData")
        try:
            handler: Handler = TseIdentifierHandler()
            with self.fileStream as file:
                while True:
                    line = file.readline()
                    newHandler: Handler = handler.handle(line.strip("\n").replace('"', ""))
                    if newHandler is not None:
                        print("switch Handler to {}".format(newHandler.handlerName))
                        self.dataFromHandler[handler.handlerName] = handler.parsedData()
                        if "TseData" == handler.handlerName:
                            self.dataFromHandler["Units"] = handler.units
                        handler = newHandler
                    if not line or isinstance(handler, EofHandler):
                        break

            if self.dataFromHandler is not None and self.dataFromHandler != {}:
                return (
                    CaliDataTse(
                        self.filename,
                        self.dataFromHandler["AdditionalData"],
                        self.dataFromHandler["TseData"],
                        self.dataFromHandler["Units"],
                    ),
                    (
                        self.dataFromHandler["CaliState"]
                        if "CaliState" in self.dataFromHandler
                        else None
                    ),
                )
            else:
                return None, "failed_reading"
        except Exception as e:
            error_message = "Error loading TSE file: " + str(e)
            print(error_message)
            return None, "failed_reading"
