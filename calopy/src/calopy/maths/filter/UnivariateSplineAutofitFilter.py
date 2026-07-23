import logging

import numpy as np
import pandas as pd
import scipy

from calopy.maths.filter.Filter import Filter

UNVAR_SPLINE_AUTOFIT = "Univariate spline - autofit"


class UnivarateSplineAutofitFilter(Filter):
    type = UNVAR_SPLINE_AUTOFIT
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.splinepss = {"s_start": 0.02, "s_end": 6, "theta": 1400}
        self.par_to_test = np.arange(self.splinepss["s_start"], self.splinepss["s_end"], 0.1)
        self.par_theta = [self.splinepss["theta"]]

    def apply(self, dataFrame):
        print("univariateSplineautofit")
        splined = {}
        for column in dataFrame:
            df, df_min, dict_min = self.grid_find_smoothing_par(dataFrame[column])
            xVal = range(0, len(dataFrame.index))
            spl = scipy.interpolate.UnivariateSpline(xVal, dataFrame[column], s=dict_min[column])
            splined[column] = pd.Series(xVal).apply(spl)
            splined[column].index = dataFrame.index
        return pd.DataFrame(splined)

    # https://data.princeton.edu/eco572/smoothing.pdf
    ### currently only works for univariate spline
    def get_pss_univariateSpline(self, ser, smoothing_par, theta):
        xVal = list(range(0, len(ser)))
        spl = scipy.interpolate.UnivariateSpline(xVal, ser, s=smoothing_par)
        y_pred = spl(xVal)

        spl2 = spl.derivative(n=2)
        pss = spl.get_residual() + theta * np.sum(
            np.power(spl2(xVal), 2)
        )  # penalized sum of squares

        n = len(ser)
        aic = n * np.log(spl.get_residual() / n) + 2 * len(spl.get_coeffs())

        return y_pred, pss, aic

    ### also used for grid search in commandsSplinepssWindow
    def grid_find_smoothing_par(self, series: pd.Series):
        pss_df = pd.DataFrame(columns=["sample", "par", "pss", "theta", "aic"])

        for th in self.par_theta:
            for par in range(len(self.par_to_test)):
                pen_sos = self.get_pss_univariateSpline(series, self.par_to_test[par], theta=th)
                add_df = pd.DataFrame(
                    [[series.name, self.par_to_test[par], pen_sos[1], th, pen_sos[2]]],
                    columns=["sample", "par", "pss", "theta", "aic"],
                )
                pss_df = pd.concat([pss_df, add_df], ignore_index=True)

                ### early stopping if converged: 3 par no change
                if (
                    par > 3
                    and len(set(pss_df.iloc[pss_df.shape[0] - 4 : pss_df.shape[0] - 1, :]["pss"]))
                    == 1
                ):
                    break

        pss_df["par"] = round(pss_df["par"], 2)

        pss_df_min = pss_df.sort_values("pss").groupby(["theta", "sample"], as_index=False).first()
        pss_dict_min = (
            pss_df_min[pss_df_min["theta"] == self.par_theta[0]]
            .set_index("sample")
            .to_dict()["par"]
        )
        return pss_df, pss_df_min, pss_dict_min

    def get_parameter_text(self):
        return ""
