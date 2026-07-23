import pandas as pd

from calopy.maths.filter.Filter import Filter


class NightAndDayFilter(Filter):
    DAY = "light"
    NIGHT = "dark"

    def __init__(self, night, day):
        self.night = night
        self.day = day

    def apply(self, dataFrame):
        nightAndDayDict = {}
        nightAndDayDict["total"] = dataFrame
        nightAndDayDict[self.NIGHT] = dataFrame.between_time(self.night, self.day)
        nightAndDayDict[self.DAY] = dataFrame.between_time(self.day, self.night)
        return pd.concat(nightAndDayDict, axis=1)

    def get_parameter_text(self):
        txt = "dark:" + str(self.night) + ",light:" + str(self.day)
        return txt
