import numpy as np
import pingouin
import scipy
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
#from patsy import Q
from patsy import ModelDesc, Term, LookupFactor

def ttest_ind(x, y):
    t_statistic, pval = scipy.stats.ttest_ind(x, y, nan_policy="omit")
    return t_statistic, pval


def linear_regression(x, y):
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    return slope, intercept, r_value, p_value, std_err


def linear_regression_pin(X, y):
    reg_mdl = pingouin.linear_regression(X, y, add_intercept=True)
    print("Pin reg out: --------------------------------------------------")
    print(reg_mdl)
    return reg_mdl


def pearson_correlation(x, y):
    corr_coef, corr_pVal = scipy.stats.pearsonr(x, y)
    return corr_coef, corr_pVal


# https://mcfromnz.wordpress.com/2011/03/02/anova-type-iiiiii-ss-explained/
def ancova(data, dv, covar, between):
    pythonic_df = data.copy(deep=True)
    pythonic_df.columns = [replaceSpecialChars(x) for x in pythonic_df.columns.tolist()]

    ### y ~ x + group + x:group
    ancovaFormula = (
        replaceSpecialChars(dv)
        + " ~ "
        + replaceSpecialChars(covar)
        + " + "
        + replaceSpecialChars(between)
        + " + "
        + replaceSpecialChars(covar)
        + ":"
        + replaceSpecialChars(between)
    )

    model = smf.ols(ancovaFormula, pythonic_df).fit()
    aov_table = anova_lm(model, typ=2)
    return aov_table, ancovaFormula


# penguin version
def calopy_ancova(data, dv, covar, between):
    aov = pingouin.ancova(data=data, dv=dv, covar=covar, between=between)
    return aov

def calopy_ancova_full_model(data, dv, covar, between):
    formula_text = f"Q('{dv}') ~ Q('{covar}') * Q('{between}')"
    model = smf.ols(formula=formula_text, data=data)
    lm_ancovafull = model.fit()
    full_model_result_table = pd.DataFrame(lm_ancovafull.summary2().tables[1])
    full_model_result_table.insert(0, "Parameter", full_model_result_table.index)
    full_model_result_table = full_model_result_table.reset_index(drop=True)
    full_model_result_table["Parameter"] = full_model_result_table["Parameter"].str.replace(r"Q\('([^']+)'\)", r"\1", regex=True)
    return full_model_result_table

def calopy_regression(predictive_var, dependent_var):  # (data, predictive_var, dependent_var)
    aov = pingouin.linear_regression(predictive_var, dependent_var, remove_na=True)
    return aov


def calopy_regression_predict(x_data, coefs):
    y_data = coefs[1] * x_data + coefs[0]
    return y_data


def anova(data, dv, between, is_day_night=False, is_welch=False):
    if is_day_night:
        data = day_night_data_split(data)
    if is_welch:
        print("yes")
        aov = pingouin.welch_anova(data=data, dv=dv, between=between)
    else:
        print("No")
        aov = pingouin.anova(data=data, dv=dv, between=between, detailed=False)
    return aov


def day_night_data_split(data):
    return data[data.temp_condition != "total"]


def rm_anova(data, dv, within, subject):
    aov = pingouin.rm_anova(data=data, dv=dv, within=within, subject=subject, detailed=False)
    return aov


def mixed_anova(data, dv, within, between, subject):
    aov = pingouin.mixed_anova(data=data, dv=dv, within=within, between=between, subject=subject)
    return aov


def pairwise_ttests(data, dv, within, between, subject):
    posthocs = pingouin.pairwise_tests(data=data, dv=dv, within=within, subject=subject)
    return posthocs


# dependent variable Y is response
# positive lag: first ser lags second, is behind it
# https://currents.soest.hawaii.edu/ocn_data_analysis/_static/SEM_EDOF.html#Cross-correlation
def cross_correlation(x_seq, y_seq, maxLagLimit):
    y2 = x_seq  # first
    y1 = y_seq  # response

    lagPos = np.arange(-len(y2) + 1, len(y2))
    ccov = np.correlate(y1 - y1.mean(), y2 - y2.mean(), mode="full")
    ccor = ccov / (len(y2) * y1.std() * y2.std())
    lagArea = ccor[len(y2) - 1 : len(y2) + maxLagLimit]  # only to maxLagPos
    maxLagPos = np.argmax(lagArea)
    maxCor = lagArea[maxLagPos]

    return lagPos, ccor, maxLagPos, maxCor


# replace special characters [for anova]
def replaceSpecialChars(text):
    chars = "!@#$%^&*()[]{};,./<>?|`~-=+:~\ "
    for c in chars:
        text = text.replace(c, "_")
    return text


def rmr_without_activity_data():
    pass
