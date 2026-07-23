import pandas as pd
import pingouin

from calopy.maths import statistic


def rm_anova_statistics(sliced_data):
    if not isinstance(sliced_data, pd.DataFrame):
        raise ValueError("Data must be a Pandas DataFrame.")
    aov = pingouin.rm_anova(
        data=sliced_data,
        dv="feature",
        within="sample",
        subject="condition",
        detailed=False,
    )
    return aov


def mixed_anova_statistics(sliced_data):
    if not isinstance(sliced_data, pd.DataFrame):
        raise ValueError("Data must be a Pandas DataFrame.")
    stats_mixed_anova = statistic.mixed_anova(
        data=sliced_data,
        dv="feature",
        within="condition",
        subject="sample",
        between="group",
    )
    return stats_mixed_anova


def paired_ttest_statistics(sliced_data):
    if not isinstance(sliced_data, pd.DataFrame):
        raise ValueError("Data must be a Pandas DataFrame.")
    test_results = pingouin.pairwise_tests(
        data=sliced_data, dv="feature", within="condition", subject="sample"
    )
    return test_results
