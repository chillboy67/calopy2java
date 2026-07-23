import datetime
import itertools
import logging
import re
import string

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_string_dtype

from calopy.data.DataFilter import DataFilter
from calopy.maths.dataframe_utils import convertDataFrameCorrectType, \
                                         getDefaultValueTypeDataFrame, \
                                         replaceNaNvaluesInDataFrame
from calopy.maths.filter.GeneralizedAdditiveFilter import GeneralizedAdditiveFilter
from calopy.maths.series_utils import getTimestepsPerDayFromIndex, parse_date_times


class CaliDataTse:
    logger = logging.getLogger(__name__)

    def __init__(self, name: string, additionalData, measurementData, units):
        print("CaliDataTse_init")
        self.units = units
        self.name = name
        self.additionalData = None
        self.setAdditionalData(additionalData)
        self.measurementData = measurementData
        self.data = self.indexByDate(measurementData)
        self.filter = DataFilter(self.measurements())
        self.excludedSamples = []
        self.groupedBy = self.getCategoricalColumns()[0]
        self.croppedStart = self.data.index[0]
        self.croppedEnd = self.data.index[-1]
        self.night = datetime.datetime.strptime("18:00", "%H:%M").time()
        self.day = datetime.datetime.strptime("06:00", "%H:%M").time()
        self.allSameDayStart = False
        self.plotXlabelDay = "date"

    def measurementFilteredGroupedDateTimeIndexed(self, label):
        print("calidata: measurementFilteredGroupedDateTimeIndexed")
        rawData = self.measurementGroupedDateTimeIndexed(label)
        return self.filter.filter(label, rawData)

    def measurementFilteredDateTimeIndexed(self, label):
        print("calidata: measurementFilteredDateTimeIndexed")
        rawData = self.measurementDateTimeIndexed(label)
        return self.filter.filter(label, rawData)

    def measurementGroupedDateTimeIndexed(self, label):
        print("calidata: measurementGroupedDateTimeIndexed")
        data = self.measurementDateTimeIndexed(label)
        groupedData = self.doGrouping(data.astype("float"), self.groupedBy).interpolate(
            method="linear", limit=5, limit_area="inside"
        )
        return groupedData

    def measurementAndFiltered(self, label):
        groupedData = self.doGroupingByColumns(
            self.measurementDateTimeIndexed(label), self.groupedBy
        )
        groupedData = self.filter.filter(label, groupedData)
        return groupedData

    def measurementDateTimeIndexed(self, label):
        print("calidata: measurementDateTimeIndexed")
        data = self.data
        measurementData: pd.DataFrame = data.xs(label, level="measurements", axis=1)

        # Filter out columns that are not present in measurementData
        existing_columns = [col for col in self.excludedSamples if col in measurementData.columns]
        sampleExcludedData = measurementData.drop(columns=existing_columns, axis=1)

        if self.allSameDayStart:
            sampleExcludedData = self.make_samples_start_same_day(sampleExcludedData)

        croppedData = sampleExcludedData[
            (sampleExcludedData.index > self.croppedStart)
            & (sampleExcludedData.index <= self.croppedEnd)
        ]
        return croppedData.astype("float")

    def measurements(self):
        measurements = []
        for column in self.data.columns.levels[1]:
            try:
                frame: pd.DataFrame = self.data.xs(column, level="measurements", axis=1).astype(
                    "float"
                )
                measurements.append(column)
            except:
                print("Column", column, "is not of type float.")

        # TODO: Check what this was for (Helin)
        # Optionally add 'diet_kcal/g' if it is set in additionalData and not 'add_value'
        # if (
        #     hasattr(self, 'additionalData') and self.additionalData is not None and
        #     'diet_kcal/g' in self.additionalData.columns and
        #     any(self.additionalData['diet_kcal/g'] != 'add_value')
        # ):
        #     if 'diet_kcal/g' not in measurements:
        #         measurements.append('diet_kcal/g')
        return measurements

    def samples(self):
        return self.data.columns.levels[0].tolist()

    def samplesWithoutExcluded(self):
        samples = self.samples()
        return [x for x in samples if x not in self.excludedSamples]

    def doGrouping(self, dataForGrouping, groupingBy):
        print("calidata: doGrouping")
        groups = set(self.additionalData[groupingBy])
        dict_of_groups = {}
        for group in groups:
            boxes = self.additionalData[self.additionalData[groupingBy] == group]["box"]
            dataSeriesDict = {}
            for box in boxes:
                if box in dataForGrouping:
                    dataSeriesDict[box] = dataForGrouping[box]
            if len(dataSeriesDict.keys()) > 0:
                dict_of_groups[group] = pd.concat(dataSeriesDict, axis="columns").mean(axis=1)
        dataFrame = pd.concat(dict_of_groups, axis=1)
        return dataFrame

    def doGroupingTwoFactors(self, dataForGrouping, groupingByFirst, groupingBySecond):
        print("calidata: doGrouping by 2 factors")
        groups1 = set(self.additionalData[groupingByFirst])
        groups2 = set(self.additionalData[groupingBySecond])

        dict_of_groups1 = {}
        dict_of_groups2 = {}
        list_of_dataframes = []

        for grp1, grp2 in itertools.product(groups1, groups2):
            boxes = self.additionalData[
                (self.additionalData[groupingByFirst] == grp1)
                & (self.additionalData[groupingBySecond] == grp2)
            ]["box"]

            dataSeriesDict = {}
            for box in boxes:
                if box in dataForGrouping:
                    dataSeriesDict[box] = dataForGrouping[box]

            if len(dataSeriesDict.keys()) > 0:
                # print(pd.concat(dataSeriesDict, axis="columns").mean(axis=1))
                dict_of_groups1[grp1] = pd.concat(dataSeriesDict, axis="columns").mean(axis=1)
                dict_of_groups2[grp2] = pd.concat(dataSeriesDict, axis="columns").mean(axis=1)

            # TODO: this can be done better:
            df1 = pd.DataFrame(dict_of_groups1)
            df1[groupingByFirst] = grp1
            df1 = df1[[groupingByFirst, grp1]]
            df1.set_index(groupingByFirst).stack()
            df1.columns = [groupingByFirst, "value"]

            df2 = pd.DataFrame(dict_of_groups2)
            df2[groupingBySecond] = grp2
            df2 = df2[[groupingBySecond, grp2]]
            df2.set_index(groupingBySecond).stack()
            df2.columns = [groupingBySecond, "value"]

            df2 = df2.drop(columns=["value"])
            list_of_dataframes.append(pd.concat([df1, df2], axis=1))
        dataFrame = pd.concat(list_of_dataframes)
        return dataFrame

    def doGroupingByIndex(self, dataForGrouping, groupingBy):
        print("calidata: doGroupingByIndex")
        groups = set(self.additionalData[groupingBy])
        indexed_by_groups = {}
        for group in groups:
            boxes = self.additionalData[self.additionalData[groupingBy] == group]["box"]
            dataFrame = dataForGrouping[dataForGrouping.index.isin(boxes)]
            indexed_by_groups[group] = dataFrame
        return pd.concat(indexed_by_groups, axis=1)

    def doGroupingByColumns(self, dataForGrouping, groupingBy):
        print("calidata: doGroupingByColumns")
        groups = set(self.additionalData[groupingBy])
        columns_by_groups = {}
        for group in groups:
            boxes = self.additionalData[self.additionalData[groupingBy] == group]["box"]
            dataFrame = dataForGrouping.loc[:, dataForGrouping.columns.isin(boxes)]
            columns_by_groups[group] = dataFrame
        return pd.concat(columns_by_groups, axis=1, keys=columns_by_groups.keys())

    def setGrouping(self, groupedBy):
        self.groupedBy = groupedBy

    def setAdditionalData(self, additionalData, typeDict=None):
        print("calidata: setAdditionalData")
        if additionalData is not None and additionalData.shape[1] > 1:
            if typeDict is None:
                typeDict = getDefaultValueTypeDataFrame(additionalData)
            print(f"Type Dictionary: {typeDict}")
            self.additionalData = convertDataFrameCorrectType(additionalData, typeDict)
            self.additionalData["box"] = self.additionalData["box"].astype(str)
            print("Updated additional_data with correct types")

            # Add diet kcal Column
            if "diet_kcal/g" not in self.additionalData.columns:
                self.additionalData["diet_kcal/g"] = "add_value"
            print("Diet kcal/g added to metadata")

    def getCategoricalColumns(self):
        if self.additionalData is None:
            return []
        else:
            categorical_columns = [
                col
                for col in self.additionalData.columns
                if is_string_dtype(self.additionalData[col])
            ]
            return categorical_columns

    def getContinuousColumns(self):
        if self.additionalData is None:
            return []
        else:
            continuous_columns = [
                col
                for col in self.additionalData.columns
                if is_numeric_dtype(self.additionalData[col])
            ]
            return continuous_columns

    def getContinuousColumnIndexedByBox(self, column):
        try:
            print("getContinuousColumnIndexedByBox:" + column)
            series = self.additionalData.set_index("box")[column]
            series.name = None
            return series
        except KeyError:
            print(f"Column {column} not found in the data.")
            return pd.Series()

    def indexByDate(self, data):
        dateTimeIndexedDict = {}
        for box in data.columns.levels[0].tolist():
            dataFrame = data[box].replace("", pd.NA).dropna(thresh=3)  # date,time + 1 measurement present
            dateTimeSeries = parse_date_times(
                dataFrame.loc[:, "date"].astype(str) + " " + dataFrame.loc[:, "time"].astype(str)
            )
            dataFrame.set_index(dateTimeSeries, inplace=True)
            dateTimeIndexedDict[box] = dataFrame
        resultDataFrame = pd.concat(dateTimeIndexedDict, axis=1, names=["boxes", "measurements"])
        replaceNaNvaluesInDataFrame(resultDataFrame)
        resultDataFrame = self.add_cumulative_columns(resultDataFrame)
        resultDataFrame.rename_axis(index="datetime", inplace=True)
        return resultDataFrame

    def shiftToDate(self, shiftDate: datetime.datetime):
        shiftedDataDict = {}
        for box in self.data.columns.levels[0].tolist():
            dataFrame = self.data[box]
            dateSeries = (
                dataFrame.loc[:, "date"]
                .dropna()
                .map(
                    lambda date: datetime.datetime.strptime(
                        "".join(c for c in date if c.isnumeric()), "%d%m%Y"
                    ).date()
                )
            )
            delta = dateSeries.iloc[0] - shiftDate.date()
            dataFrame.loc[:, "date"] = dateSeries.map(
                lambda date: (date - delta).strftime("%d-%m-%Y")
            )
            shiftedDataDict[box] = dataFrame
        resultDataFrame = pd.concat(shiftedDataDict, axis=1, names=["boxes", "measurements"])
        return resultDataFrame

    def length(self):
        indexAsList = self.data.index.tolist()
        return len(
            indexAsList[indexAsList.index(self.croppedStart) : indexAsList.index(self.croppedEnd)]
        )

    def timestepsPerDay(self):
        indexAsList = self.data.index.tolist()
        indexAsListCropped = indexAsList[
            indexAsList.index(self.croppedStart) : indexAsList.index(self.croppedEnd)
        ]
        timestepsPerDay = getTimestepsPerDayFromIndex(indexAsListCropped)
        return timestepsPerDay

    def setNightAndDay(self, night, day):
        self.night = night
        self.day = day

    def setExcludedSamples(self, excludedSamples):
        self.excludedSamples = excludedSamples

    def setAllSameDayStart(self, allSameDayStart):
        self.allSameDayStart = allSameDayStart

    def setPlotXlabelDay(self, plotXlabelDay):
        self.plotXlabelDay = plotXlabelDay

    def is_cumulative(self, data):
        dataAsFloat = pd.to_numeric(data, errors="coerce")
        for i in range(1, len(dataAsFloat)):
            if dataAsFloat.iloc[i] < dataAsFloat.iloc[i - 1]:
                return False
        return True

    def make_non_cumulative(self, cumulative_data):
        non_cumulative = [cumulative_data.iloc[0]]
        for i in range(1, len(cumulative_data)):
            non_cumulative.append(cumulative_data.iloc[i] - cumulative_data.iloc[i - 1])
        return non_cumulative

    def add_cumulative_columns(self, df):
        cumulative_pattern = re.compile(r"(feed|food|drink|water|intake)", re.IGNORECASE)
        for column in df.columns:
            if re.search(cumulative_pattern, column[1]):
                if self.is_cumulative(df[column]):
                    df[(column[0], column[1] + " non cumulative")] = self.make_non_cumulative(
                        pd.to_numeric(df[column], errors="coerce")
                    )
                else:
                    df[(column[0], column[1] + " cumulative")] = pd.to_numeric(
                        df[column], errors="coerce"
                    ).cumsum()
        df.sort_index(axis=1, inplace=True, level="boxes", sort_remaining=False)
        return df

    def remove_measurement_name_from_data(self, measurement_name):
        self.data.drop(columns=measurement_name, axis=1, inplace=True, errors="ignore", level=1)

    def add_measurement_to_data(self, df, measurement_name):
        self.remove_measurement_name_from_data(measurement_name)
        if not df.isna().all().all():
            second_level_index = pd.MultiIndex.from_product(
                [df.columns, [measurement_name]], names=["boxes", "measurements"]
            )
            df.columns = second_level_index
            self.data = pd.concat([self.data, df], axis=1)
        self.data.sort_index(axis=1, inplace=True, level="boxes", sort_remaining=False)
        self.filter.addMeasurement(measurement_name)

    def make_samples_start_same_day(self, df):
        def shift_sample_start_day(df, sample_col):
            earliest_timestamp = df.index[0]
            first_valid_index = df[sample_col].first_valid_index()
            day_difference_td = first_valid_index - earliest_timestamp

            def days_hours_minutes(td):
                return [td.days, td.seconds // 3600, (td.seconds // 60) % 60]

            day_difference_list = days_hours_minutes(day_difference_td)

            if day_difference_list[1] >= 22:  ## 2 hours tolerance for old day
                day_difference_list[0] = day_difference_list[0] + 1
            df[sample_col].index = df[sample_col].index - datetime.timedelta(
                days=day_difference_list[0]
            )
            return df[sample_col]

        shifted_sample_cols = {}
        for sample_col in df.columns.difference(["datetime"]):
            shifted_sample_cols[sample_col] = shift_sample_start_day(df, sample_col)
        shifted_df = pd.concat(shifted_sample_cols, axis=1)
        shifted_df = shifted_df.loc[shifted_df.first_valid_index() : shifted_df.last_valid_index()]
        return shifted_df

    def dataToShowDateTimeIndexedDaySplit(self, label):
        print("### debug dataToShowDateTimeIndexedDaySplit")
        tmp_grouping = self.groupedBy
        self.setGrouping("box")
        data_df = self.measurementFilteredDateTimeIndexed(label)
        data_df_daysplit = self.addDaySplitIndex(data_df)
        # data_df_daysplit = self.getOnlyCompleteDaySplit(data_df_daysplit)
        data_df_daysplit["time"] = data_df_daysplit.index.get_level_values("datetime").time
        data_df_daysplit = data_df_daysplit.set_index("time", append=True).droplevel("datetime")
        data_df_daysplit = data_df_daysplit.unstack(level="day_split")
        self.setGrouping(tmp_grouping)
        data_df_daysplit = self.addGrouping(data_df_daysplit, self.groupedBy)
        print(data_df_daysplit)
        return data_df_daysplit
