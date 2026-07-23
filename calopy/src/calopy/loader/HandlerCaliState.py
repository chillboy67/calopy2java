from calopy.loader.handler import Handler
from calopy.loader.HandlerEof import EofHandler


class CaliStateHandler(Handler):
    def __init__(self, seperator):
        self.handlerName = "CaliState"
        self.validateAndHandle = self.parseHeader
        self.sep = seperator
        self.tseFilter = {}
        self.tseState = {}
        self.caliState = {}

    def parsedData(self):
        print("parsedData from CaliStateHandler")
        return {
            "tseFilter": self.tseFilter,
            "tseState": self.tseState,
            "caliState": self.caliState,
        }

    def handle(self, line):
        print("handle {line}".format(line=line))
        if line == "":
            return EofHandler()
        return self.validateAndHandle(line)

    def parseHeader(self, line):
        if line == "calopy TseState":
            self.validateAndHandle = self.parseTseState
        return None

    def parseTseState(self, line):
        if line == "Filter:":
            self.validateAndHandle = self.parseCaliFilter
        return None

    def parseCaliFilter(self, line):
        if line == "Other:":
            self.validateAndHandle = self.parseOther
        else:
            try:
                key, value, param, outlierFunc, outlierDev = line.split(self.sep)
                self.tseFilter[key] = [value, param, outlierFunc, outlierDev]
            except Exception as e:
                print(e)
        return None

    def parseOther(self, line):
        if line == "calopy CaliState":
            self.validateAndHandle = self.parseCaliState
        else:
            try:
                key, value = line.split(self.sep)
                self.tseState[key] = value
            except Exception as e:
                print(e)

        return None

    def parseCaliState(self, line):
        if line == "":
            return EofHandler()
        try:
            # split line by sep and assign first value to key, second to type and the rest to value
            key, type, value = line.split(self.sep, 2)
            self.caliState[key] = [type, value]
        except Exception as e:
            print(e)
        return None
