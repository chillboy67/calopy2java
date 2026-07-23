import re
from math import isnan

import numpy as np
import pandas as pd
from dateutil import parser
from pandas.api.types import is_numeric_dtype, is_string_dtype


def getIdxWhereValuesChange(limitsSeries):
    result = []
    observed = limitsSeries.iloc[0]
    for index, value in limitsSeries.items():
        if value != observed:
            result.append(index)
            observed = value
    return result


def getIndexOf24HourInterval(series: pd.DatetimeIndex):
    timesteps_per_day = getTimestepsPerDayFromIndex(series)
    results_24h_intervals = series[::timesteps_per_day].tolist()
    results_24h_intervals = results_24h_intervals[1:]
    return results_24h_intervals


def getAreasWhereDatetimIndexIs(data, func):
    toSeries = pd.Series(data.index.tolist())
    areas = getAreasWhereValuesAre(toSeries, func)
    result = []
    for tuple in areas:
        result.append((toSeries[tuple[0]], toSeries[tuple[1]]))
    return result


def getAreasWhereValuesAre(data, func):
    start, end = None, None
    result = []
    withInAreaFlag = func(data.iloc[0])
    if withInAreaFlag:
        start = data.index[0]
    for index, value in data.items():
        if func(value):
            if not withInAreaFlag:
                start = index
                withInAreaFlag = True
        else:
            if withInAreaFlag:
                end = index
                result.append((start, end))
                start, end = None, None
                withInAreaFlag = False
    if start and not end:
        result.append((start, data.index[-1]))
    return result


def getDefaultValueTypeSeries(series: pd.Series):
    if not is_string_dtype(series) and not is_numeric_dtype(series):
        return "NA"
    series = series.replace(
        ["", "-", "NA", "na", "NAN", "Nan", "NaN", "nan", "NULL", "Null", "null"],
        np.nan,
    )
    num_unique_values = series.nunique(dropna=False)
    try:
        # series = to_numeric(series,errors="ignore")
        series = pd.to_numeric(series)
    except:
        print("Error when calling to_numeric on series")

    if is_numeric_dtype(series):
        return "numeric"
    elif series.dtype == "bool":
        return "character"
    else:
        return "character"


def convertSeriesCorrectType(series: pd.Series, dataType):
    if dataType == "numeric":
        return pd.to_numeric(series, errors="coerce")
    elif dataType == "character":
        return series.astype(str)
    else:
        return pd.Series([np.nan] * series.size)


def getTimestepsPerDayFromIndex(datecolumn_index):
    indexAsList = datecolumn_index

    ### daysplit df only contains datetime.time elements
    if isinstance(indexAsList, pd.Index) and indexAsList.dtype != "datetime64[ns]":
        indexAsList = pd.to_datetime("1995-04-11" + " " + indexAsList.astype(str), utc=True)

    timeDiff = indexAsList[1] - indexAsList[0]
    timeDiffMinutes = timeDiff.total_seconds() / 60
    timestepsPerDay = int(1440 / timeDiffMinutes)
    return timestepsPerDay

def get_time_sampling_interval_for_variable(input_var):
    dt_index = input_var.index
    time_deltas = pd.Series(dt_index).diff()
    time_deltas_minutes = time_deltas.dt.total_seconds() / 60

    if isnan(time_deltas_minutes.iloc[0]):
        time_deltas_minutes.iloc[0] = time_deltas_minutes.iloc[1]

    time_deltas_minutes = pd.Series(
        time_deltas_minutes.values,
        index=input_var.index  # match with df rows after first
    )

    return time_deltas_minutes



def parse_date_times(date_series: pd.Series):
    ### check format if user date input is wrong - which parse create less NaT
    parsed_dayfirst = pd.to_datetime(pd.Series(date_series), errors="coerce", dayfirst=True)
    nat_count_dayfirst = parsed_dayfirst.isna().sum()
    parsed_monthfirst = pd.to_datetime(pd.Series(date_series), errors="coerce", dayfirst=False)
    nat_count_monthfirst = parsed_monthfirst.isna().sum()
    if nat_count_dayfirst <= nat_count_monthfirst:
        parsed_date_series = parsed_dayfirst
    else:
        parsed_date_series = parsed_monthfirst
    
    ### safety check again for correct day/month order
    def check_failed_date_parsing(date_series):
        date_series = date_series.dropna()
        day_changes = date_series.dt.day.diff().fillna(0) != 0
        month_changes = date_series.dt.month.diff().fillna(0) != 0
        day_change_count = day_changes.sum()
        month_change_count = month_changes.sum()
        return month_change_count > day_change_count

    if check_failed_date_parsing(parsed_date_series):
         parsed_date_series = pd.to_datetime(pd.Series(date_series), errors="coerce", dayfirst=False)
    return parsed_date_series


def find_label_in_list(input_list, search_term):
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    for item in input_list:
        if pattern.search(item):
            return item
    return input_list[0] if input_list else None
