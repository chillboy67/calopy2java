import numpy as np
import pandas as pd
import scipy
from scipy.integrate import simps
from scipy.signal import find_peaks

from calopy.maths.daysplit_utils import addDaySplitIndex, getDaySplitDf
from calopy.maths.series_utils import getTimestepsPerDayFromIndex, parse_date_times

### feature extraction methods


def extract_feature_df_rawdata(df, **kwargs):
    feature_df = df.stack(future_stack=True).stack(future_stack=True).reset_index()
    feature_df.columns = ["index", "box", "group", "value"]
    feature_df["feature"] = RAW_DATA
    feature_df["day_split"] = "all"
    feature_df = feature_df[["box", "group", "day_split", "feature", "value", "index"]]
    return feature_df


def extract_feature_mean(series, **kwargs):
    value = series.mean()
    index = (series - value).abs().idxmin() if pd.notnull(value) else None
    return value, index


def extract_feature_sum(series, **kwargs):
    value = series.sum()
    index = None
    return value, index


def extract_feature_median(series, **kwargs):
    value = series.median()
    index = (series - value).abs().idxmin() if pd.notnull(value) else None
    return value, index


def extract_feature_min(series, **kwargs):
    value = series.min()
    index = series.idxmin() if pd.notnull(value) else None
    return value, index


def extract_feature_max(series, **kwargs):
    value = series.max()
    index = series.idxmax() if pd.notnull(value) else None
    return value, index


def extract_feature_auc(series, **kwargs):
    series_woNA = series.dropna()
    ### if only time is given
    series_index_str = series_woNA.index.astype(str)
    if series_index_str.str.fullmatch(r"\d{2}:\d{2}:\d{2}").all():
       series_woNA.index = "2000-01-01 " + series_index_str
    series_woNA.index = parse_date_times(series_woNA.index)
    time_index = (series_woNA.index - series_woNA.index[0]).total_seconds()/3600
    value = scipy.integrate.simps(y = series_woNA, x=time_index, **kwargs)
    index = None
    return value, index


def extract_feature_amplitude(series, **kwargs):
    feature_max = extract_feature_max(series)
    feature_min = extract_feature_min(series)
    value = feature_max[0] - feature_min[0]
    index = [feature_max[1], feature_min[1]]
    return value, index


def extract_feature_max_peak(series, **kwargs):
    ### from https://pubmed.ncbi.nlm.nih.gov/30773466/
    ### min peak prominence of 2 sd of the signal, min peak distance of 6 h, min peak height as signal mean level
    limit_mean_level = series.mean()
    limit_prominence = 2 * series.std()
    limit_daylength = (
        getTimestepsPerDayFromIndex(series.index) * 0.75
    )  ### 18 hours distance between peaks

    peak_indices, _ = scipy.signal.find_peaks(
        series,
        prominence=limit_prominence,
        height=limit_mean_level,
        distance=limit_daylength,
        **kwargs,
    )
    if len(peak_indices) > 0:
        peak_values = series.iloc[peak_indices].tolist()
        peak_indices = series.index[peak_indices].tolist()
    else:
        peak_values = [np.nan]
        peak_indices = [None]
    return peak_values, peak_indices


def extract_feature_min_peak(series, **kwargs):
    limit_mean_level = series.mean()
    limit_prominence = 2 * series.std()
    limit_daylength = (
        getTimestepsPerDayFromIndex(series.index) * 0.75
    )  ### 18 hours distance between peaks
    inverted_series = -series
    peak_indices, _ = scipy.signal.find_peaks(
        inverted_series,
        prominence=limit_prominence,
        height=-limit_mean_level,
        distance=limit_daylength,
        **kwargs,
    )
    if len(peak_indices) > 0:
        peak_values = series.iloc[peak_indices].tolist()
        peak_indices = series.index[peak_indices].tolist()
    else:
        peak_values = [np.nan]
        peak_indices = [None]
    return peak_values, peak_indices


def extract_feature_stats_df(df, feature, daysplit=False, **kwargs):
    print("extract_feature_stats_df")

    if daysplit:
        df_raw = df.copy()
        df = getDaySplitDf(df)

    results = []
    for column in df.columns:
        value, index_value = BASE_FEATURES[feature](df[column], **kwargs)

        if not isinstance(value, list):
            value = [value]
        if not isinstance(index_value, list):
            index_value = [index_value]

        if daysplit:
            group, box, day_split = column
        else:
            group, box = column
            day_split = "all"

        for val, idx in zip(value, index_value):
            results.append([box, group, day_split, feature, val, idx])

    result_df = pd.DataFrame(
        results, columns=["box", "group", "day_split", "feature", "value", "index"]
    )

    ### if daysplit add correct day to index again
    if daysplit:
        result_df["index"] = result_df["index"].astype(str)
        tmp_df_split = addDaySplitIndex(df_raw)
        tmp_df = pd.DataFrame(
            {
                "time": tmp_df_split.index.get_level_values("datetime").time.astype(str),
                "day_split": tmp_df_split.index.get_level_values("day_split"),
                "datetime": tmp_df_split.index.get_level_values("datetime"),
            }
        )
        merged_df = pd.merge(
            result_df,
            tmp_df,
            left_on=["index", "day_split"],
            right_on=["time", "day_split"],
            how="left",
        )
        merged_df["index"] = merged_df["datetime"]
        result_df = merged_df.drop(columns=["time", "datetime"])

    return result_df


def extract_feature_stats_df_daywise_median(feature_df):
    median_df = (
        feature_df.groupby("box")
        .agg(
            {
                "group": "first",
                "day_split": "first",
                "feature": "first",
                "value": "median",
                "index": "first",  # Retain the first 'index' (timestamp)
            }
        )
        .reset_index()
    )
    return median_df


RAW_DATA = "raw data"
TOTAL = "cumulative total"
AUC = "AUC"
MEAN = "mean"
MEDIAN = "median"
MIN = "minimum"
MAX = "maximum"
AMPLITUDE = "amplitude (max - min)"
MIN_PEAK = "minimum peak"
MAX_PEAK = "maximum peak"

BASE_FEATURES = {
    TOTAL: extract_feature_sum,
    AUC: extract_feature_auc,
    MEAN: extract_feature_mean,
    MEDIAN: extract_feature_median,
    MIN: extract_feature_min,
    MAX: extract_feature_max,
    AMPLITUDE: extract_feature_amplitude,
    MAX_PEAK: extract_feature_max_peak,
    MIN_PEAK: extract_feature_min_peak,
}

FEATURE_FUNC_DICT = {RAW_DATA: lambda x: extract_feature_df_rawdata(x)}

FEATURE_FUNC_DICT.update(
    {
        feature_name: lambda df, feature_name=feature_name: extract_feature_stats_df(
            df, feature_name, daysplit=False
        )
        for feature_name in BASE_FEATURES
    }
)

FEATURE_FUNC_DICT.update(
    {
        f"{feature_name} (daysplit)": lambda df, feature_name=feature_name: extract_feature_stats_df(
            df, feature_name, daysplit=True
        )
        for feature_name in BASE_FEATURES
    }
)

FEATURE_FUNC_DICT.update(
    {
        f"{feature_name} (daysplit+median)": lambda df, feature_name=feature_name: extract_feature_stats_df_daywise_median(
            extract_feature_stats_df(df, feature_name, daysplit=True)
        )
        for feature_name in BASE_FEATURES
    }
)


def get_input_selectize_feature_func_dict(remove_raw_data=False):
    features = list(FEATURE_FUNC_DICT.keys())
    if remove_raw_data and RAW_DATA in features:
        features.remove(RAW_DATA)
    feature_without_daysplit = {f: f for f in features if "daysplit" not in f}
    feature_daysplit = {f: f for f in features if "(daysplit)" in f}
    feature_daysplit_and_median = {f: f for f in features if "(daysplit+median)" in f}
    raw_feature_select_choices = {
        "global": feature_without_daysplit,
        "24h split": feature_daysplit,
        "24h split and median": feature_daysplit_and_median,
    }
    return raw_feature_select_choices
