"""
生成 calojava 单元测试用的扩展参考结果：python_extended_result.csv。

覆盖 example_csv.csv 原有对比没测到的情况：
- RER 列（数值约 0.9，样条在 s=1 时真正起平滑作用）
- 偶数窗口（Calopy 界面允许的最小窗口是 2）
- VO2(3) 上更大的 s
- 含缺失值的输入（开头 5 行和第 100-109 行置空）

在 calopy/ 目录下运行：python generate_extended_reference.py
"""
import contextlib
import io
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "src"))

from calopy.maths.filter.GeneralizedAdditiveFilter import GeneralizedAdditiveFilter  # noqa: E402
from calopy.maths.filter.RollingWindowGausianFilter import RollingWindowGausianFilter  # noqa: E402
from calopy.maths.filter.RollingWindowMeanFilter import RollingWindowMeanFilter  # noqa: E402
from calopy.maths.filter.RollingWindowTriangularFilter import RollingWindowTriangularFilter  # noqa: E402
from calopy.maths.filter.SavgolFilter import SavgolFilter  # noqa: E402
from calopy.maths.filter.SingleComponentCosinorFilter import SingleComponentCosinorFilter  # noqa: E402
from calopy.maths.filter.UnivariateSplineAutofitFilter import UnivarateSplineAutofitFilter  # noqa: E402
from calopy.maths.filter.UnivariateSplineFilter import UnivariateSpline  # noqa: E402

GAP_ROWS = list(range(0, 5)) + list(range(100, 110))


def run(filter_, series):
    frame = series.to_frame("value")
    with contextlib.redirect_stdout(io.StringIO()):
        return filter_.apply(frame)["value"].reindex(series.index).values


def main():
    df = pd.read_csv(os.path.join(HERE, "..", "example_csv.csv"))
    rer = df["RER"].astype(float)
    vo2 = df["VO2(3)"].astype(float)
    gap = vo2.copy()
    gap.iloc[GAP_ROWS] = np.nan

    cases = {
        "RER": rer,
        "RER_Mean_w6": run(RollingWindowMeanFilter(6), rer),
        "RER_Triangular_w6": run(RollingWindowTriangularFilter(6), rer),
        "RER_Gaussian_w6_std2": run(RollingWindowGausianFilter(6, 2), rer),
        "RER_Savgol_w8_o3": run(SavgolFilter(8, 3), rer),
        "RER_Savgol_w9_o3": run(SavgolFilter(9, 3), rer),
        "RER_Cosinor_144": run(SingleComponentCosinorFilter(144), rer),
        "RER_GAM": run(GeneralizedAdditiveFilter(), rer),
        "RER_Spline_s1": run(UnivariateSpline(1.0), rer),
        "RER_Spline_Auto": run(UnivarateSplineAutofitFilter(), rer),
        "VO2_Mean_w4": run(RollingWindowMeanFilter(4), vo2),
        "VO2_Triangular_w4": run(RollingWindowTriangularFilter(4), vo2),
        "VO2_Gaussian_w10_std3": run(RollingWindowGausianFilter(10, 3), vo2),
        "VO2_Spline_s100": run(UnivariateSpline(100.0), vo2),
        "VO2_Spline_s500000": run(UnivariateSpline(500000.0), vo2),
        "Gap_Input": gap,
        "Gap_Mean_w5": run(RollingWindowMeanFilter(5), gap),
        "Gap_Triangular_w5": run(RollingWindowTriangularFilter(5), gap),
        "Gap_Gaussian_w5_std1": run(RollingWindowGausianFilter(5, 1), gap),
        "Gap_Savgol_w9_o3": run(SavgolFilter(9, 3), gap),
        "Gap_Cosinor_144": run(SingleComponentCosinorFilter(144), gap),
        "Gap_GAM": run(GeneralizedAdditiveFilter(), gap),
        "Gap_Spline_s10": run(UnivariateSpline(10.0), gap),
    }
    out = pd.DataFrame(cases)
    out.insert(0, "date_time", df["date_time"])
    output_file = os.path.join(HERE, "python_extended_result.csv")
    out.to_csv(output_file, index=False, float_format="%.17g")
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()
