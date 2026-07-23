import datetime

import pandas as pd

from calopy.data.CaliDataTse import CaliDataTse


class DataMerger:

    def __init__(self, caliDataTse_1: CaliDataTse, caliDataTse_2: CaliDataTse):
        self.caliDataTse_1 = caliDataTse_1
        self.caliDataTse_2 = caliDataTse_2

    def mergedData(self):
        df1 = self.shiiftDateAndRenameBoxes(self.caliDataTse_1)
        df2 = self.shiiftDateAndRenameBoxes(self.caliDataTse_2)
        concatenated = pd.concat([df1, df2], axis="columns")

        addConcatenated = pd.Series(concatenated.columns.levels[0].tolist(), name="box").to_frame()

        return CaliDataTse(
            self.caliDataTse_1.name + ":" + self.caliDataTse_2.name,
            addConcatenated,
            concatenated,
        )

    def shiiftDateAndRenameBoxes(self, caliData: CaliDataTse):
        df = caliData.shiftToDate(datetime.datetime.today()).copy(True)
        identifier = "-" + caliData.name
        columns = df.columns.levels[0]

        columnsWithIdentifier = dict(
            zip(columns, list(map(lambda colName: colName + identifier, columns)))
        )
        dfWithRenabmedColumns = df.rename(columns=columnsWithIdentifier)

        return dfWithRenabmedColumns
