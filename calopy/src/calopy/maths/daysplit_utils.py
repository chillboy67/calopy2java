import pandas as pd

from calopy.maths.filter.GeneralizedAdditiveFilter import GENERALIZED_ADDITIVE, \
                                                          GeneralizedAdditiveFilter
from calopy.maths.series_utils import getTimestepsPerDayFromIndex


def addDaySplitIndex(df):
    first_time_step = df.index[0].time()
    first_time_step_delta = pd.Timedelta(
        hours=first_time_step.hour,
        minutes=first_time_step.minute,
        seconds=first_time_step.second,
        microseconds=first_time_step.microsecond,
    )
    df_daysplit = df.groupby((df.index - first_time_step_delta).date, group_keys=False).apply(
        lambda g: g.assign(day_split=g.name)
    )
    day_dict = {day: f"day_{i+1}" for i, day in enumerate(pd.unique(df_daysplit["day_split"]))}
    df_daysplit["day_split"] = (
        pd.Categorical(df_daysplit["day_split"]).rename_categories(day_dict).astype(str)
    )
    df_daysplit.set_index("day_split", append=True, inplace=True)
    return df_daysplit


def inferDaySplitMissingValues(daysplit_df, timestepsPerDay, missingHoursAllowed):
    missing_values_per_day = (
        timestepsPerDay - daysplit_df.index.get_level_values("day_split").value_counts()
    )
    missing_values_of_last_day = missing_values_per_day.iloc[-1]
    time_diffs_in_seconds = (
        daysplit_df.index.get_level_values("datetime")
        .to_series()
        .diff()
        .dropna()
        .dt.total_seconds()
    )
    mode_diff_timedelta = pd.to_timedelta(time_diffs_in_seconds.mode()[0], unit="s")
    total_timespan = pd.Timedelta(mode_diff_timedelta * missing_values_of_last_day)
    # added AND condition to fix for 0 missing values of last day
    if total_timespan < pd.Timedelta(hours=missingHoursAllowed) and missing_values_of_last_day != 0:
        last_time = daysplit_df.index.get_level_values("datetime")[-1]
        last_day = daysplit_df.index.get_level_values("day_split")[-1]

        inferred_timesteps = [
            {
                "datetime": last_time + mode_diff_timedelta * (i + 1),
                "day_split": last_day,
            }
            for i in range(missing_values_of_last_day)
        ]
        inferred_timesteps_df = pd.DataFrame(inferred_timesteps).set_index(
            ["datetime", "day_split"]
        )
        # daysplit_df_inferred = daysplit_df.append(inferred_timesteps_df)
        daysplit_df_inferred = pd.concat([daysplit_df, inferred_timesteps_df])
        daysplit_df_inferred = GeneralizedAdditiveFilter().apply(
            daysplit_df_inferred
        )  ## best imputation method
        return daysplit_df_inferred
    else:
        return daysplit_df


def getOnlyCompleteDaySplit(df, timestepsPerDay):
    min_occurrences = timestepsPerDay
    values_per_daysplit = df.index.get_level_values("day_split").value_counts()
    complete_days = values_per_daysplit[values_per_daysplit >= min_occurrences].index
    filtered_df = df[df.index.get_level_values("day_split").isin(complete_days)]
    return filtered_df


def getDaySplitDf(df):
    daysplit_df = addDaySplitIndex(df)
    timestepsPerDay = getTimestepsPerDayFromIndex(df.index)
    daysplit_df = inferDaySplitMissingValues(daysplit_df, timestepsPerDay, missingHoursAllowed=3)
    daysplit_df = getOnlyCompleteDaySplit(daysplit_df, timestepsPerDay)
    daysplit_df["time"] = daysplit_df.index.get_level_values("datetime").time
    daysplit_df = daysplit_df.set_index("time", append=True).droplevel("datetime")
    daysplit_df = daysplit_df.unstack(level="day_split")
    return daysplit_df
