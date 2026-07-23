import logging
import os
import time

import numpy as np
import pandas as pd

from calopy.data.CaliDataCsv import CaliDataCsv
from calopy.data.CaliDataTse import CaliDataTse
from calopy.maths.dataframe_utils import replaceNaNvaluesInDataFrame
from calopy.maths.series_utils import parse_date_times


class LoaderCsv:
    logger = logging.getLogger(__name__)

    def __init__(self, filename=None, dataframe=None):
        self.filename = filename
        self.dataframe = dataframe
        if self.filename:
            print("Loading file {} on {}".format(filename, os.getcwd()))
        elif self.dataframe is not None:
            print("Loading from provided DataFrame.")

    def loadData(self):
        print("loadData")
        try:
            if self.dataframe is not None:
                df = self.dataframe.copy()  # Use provided DataFrame
            else:
                df = pd.read_csv(self.filename, na_values=["NaN"], sep=None).fillna(np.nan)

            df = df.dropna(how="all", axis="columns")  # Remove fully empty columns
            df = self.remove_row_numbers(df)
            df = df[
                df.groupby(df.columns[0])[df.columns[0]].transform("count") >= 3
                ]  # At least 3 measurement values
            self.checkCorrectFormat(df)

            additionalData = self.__getAdditionalData(df)
            measurementData = self.__getMeasurementData(df)

            return (
                CaliDataTse(self.filename if self.filename else "DataFrame", additionalData, measurementData, None),
                None,
            )
        except Exception as e:
            error_message = "Error loading data: " + str(e)
            print(error_message)
            return None, "failed_reading"

    def __convert2num(self, data: pd.DataFrame) -> pd.DataFrame:
        print("__replace NaNs convert to num")
        replaceNaNvaluesInDataFrame(data)
        data[data.columns] = data[data.columns].apply(pd.to_numeric, errors="coerce")
        return data

    def __getAdditionalData(self, df):
        date_time_index = df.columns.get_loc("date_time")
        additional_data = df.iloc[:, :date_time_index]
        additional_data.drop_duplicates(inplace=True)
        # add dummy variable if no additional data given, todo: find better solution
        if additional_data.shape[1] == 1:
            additional_data['dummy'] = 0  # Adding a dummy column with default value 0
        additional_data.reset_index(drop=True, inplace=True)
        additional_data.rename(columns={additional_data.columns[0]: "box"}, inplace=True)
        return additional_data

    def __getMeasurementData(self, df):
        date_time_index = df.columns.get_loc("date_time")
        data = df.iloc[:, :1].join(df.iloc[:, date_time_index:])
        data.rename(columns={data.columns[0]: "box"}, inplace=True)
        data.iloc[:, 2:] = self.__convert2num(data.iloc[:, 2:])

        ### uniform time interval
        print("make uniform interval")
        self.make_uniform_time_interval_optimized(data)
        data_aggregated = data
        data_aggregated["date_time"] = parse_date_times(data_aggregated["date_time"].astype(str))
        data_aggregated = data_aggregated.pivot_table(
            index="date_time", columns="box", aggfunc="mean"
        )
        data_aggregated = data_aggregated.swaplevel(axis=1).sort_index(axis=1)
        ### add date and time
        print("add time and date")
        data_aggregated = pd.concat(
            {
                box: data_aggregated[box].assign(
                    date=data_aggregated.index.date, time=data_aggregated.index.time
                )
                for box in data_aggregated.columns.get_level_values(0)
            },
            axis=1,
        )

        ### make box names to str
        print("make box names string")
        data_aggregated.columns = pd.MultiIndex.from_tuples(
            [(str(level1), str(level2)) for level1, level2 in data_aggregated.columns]
        )
        return data_aggregated

    def remove_row_numbers(self, df):
        if (
                pd.to_numeric(df.iloc[:, 0].values, errors="coerce") - 1
        ).tolist() == df.index.tolist():
            df = df.iloc[:, 1:]
        return df

    def checkCorrectFormat(self, df):
        if "date_time" not in df.columns:
            raise ValueError("Error reading csv file: no column date_time found")

        date_time_index = df.columns.get_loc("date_time")
        additional_data = df.iloc[:, :date_time_index]

        additional_data.drop_duplicates(inplace=True)
        if additional_data.iloc[:, 0].duplicated().any():
            raise ValueError(
                "Error reading csv file: duplicated sample_ids found in the first column"
            )

    def make_uniform_time_interval_optimized(self, df):
        df["date_time"] = parse_date_times(df["date_time"])

        # Compute the minimum time difference within each sample_id group
        df["time_diff"] = df.groupby("box")["date_time"].diff().dt.total_seconds()
        lowest_time_diff = df["time_diff"].dropna().min()
        df.drop(columns="time_diff", inplace=True)

        # Ensure there are no NaN values before rounding
        seconds_since_start = (df["date_time"] - df["date_time"].dt.normalize()).dt.total_seconds()
        # Fill NaN values with 0 to avoid conversion issues
        seconds_since_start = seconds_since_start.fillna(0)
        # Compute nearest bin, avoiding NaN issues
        nearest_bin = np.round(seconds_since_start / lowest_time_diff).astype("Int64") * lowest_time_diff
        # Ensure nearest_bin does not have NaN before conversion
        nearest_bin = nearest_bin.fillna(0).astype(int)
        df["date_time"] = df["date_time"].dt.normalize() + pd.to_timedelta(nearest_bin, unit="s")
