import numpy as np
import pandas as pd

from calopy.maths.series_utils import convertSeriesCorrectType, getDefaultValueTypeSeries


def convertDataFrameToSeries(
    df_1: pd.DataFrame, df_2: pd.DataFrame, firstColumnName, secondColumnName
):
    out = pd.DataFrame(data={firstColumnName: None, secondColumnName: None}, index=[])
    for label, content in df_1.items():
        zip = pd.concat([content, df_2[label]], axis=1, sort=False)
        reshape = pd.DataFrame(
            data={firstColumnName: zip.iloc[:, 0], secondColumnName: zip.iloc[:, 1]}
        )
        reshape.index = range(out.shape[0], out.shape[0] + df_1.shape[0])
        out = pd.concat([out, reshape], axis=0, sort=False)
    return out


def convertDataFrameCorrectType(df: pd.DataFrame, typeDict):
    for col, dataType in typeDict.items():
        df[col] = convertSeriesCorrectType(df[col], dataType=dataType)
    return df


def getDefaultValueTypeDataFrame(df: pd.DataFrame):
    col_value_dict = {df_col: getDefaultValueTypeSeries(df[df_col]) for df_col in df.columns}
    return col_value_dict


def replaceNaNvaluesInDataFrame(df: pd.DataFrame):
    nan_terms_list = [
        "#N/A",
        "#NA",
        "",
        "*",
        "-",
        ".",
        "?",
        "??",
        "???",
        "Inf",
        "MISSING",
        "Missing",
        "N/A",
        "NA",
        "NAN",
        "NONE",
        "NOTAPPLICABLE",
        "NOT_APPLICABLE",
        "NULL",
        "NaN",
        "Nan",
        "None",
        "NotApplicable",
        "NotAvailable",
        "Notavailable",
        "Unknown",
        "missing",
        "n/a",
        "na",
        "nan",
        "none",
        "not_applicable",
        "not_available",
        "notapplicable",
        "notavailable",
        "null",
        "unknown",
    ]
    df.replace(nan_terms_list, np.nan, inplace=True)
