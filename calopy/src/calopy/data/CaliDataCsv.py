import string

from pandas import DataFrame


class CaliDataCsv:
    def __init__(self, name: string, data: DataFrame):
        self.name = name
        self.data = data

    def dataToAnalyse(self):
        return self.data
