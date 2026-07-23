import pandas as pd
import numpy as np
import os
import sys

# 1. 设置路径
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from calopy.maths.filter.UnivariateSplineFilter import UnivariateSpline
    from calopy.maths.filter.UnivariateSplineAutofitFilter import UnivarateSplineAutofitFilter

    print("Spline filters imported successfully.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


def generate_spline_truth():
    file_path = r"D:\calopy2java\example_csv.csv"
    if not os.path.exists(file_path):
        print(f"Error: 文件未找到: {file_path}")
        return

    print(f"Reading: {file_path}")
    df = pd.read_csv(file_path)

    target_col = 'VO2(3)'
    data_frame_subset = df[[target_col]].copy()

    # 2. 运行 Univariate Spline (固定参数 s=10.0)
    print("Running UnivariateSpline (s=10.0)...")
    spline_filter = UnivariateSpline(10.0)
    res_spline = spline_filter.apply(data_frame_subset)

    # 3. 运行 Univariate Spline Autofit (自动参数)
    print("Running UnivariateSplineAutofit (this may take time)...")
    autofit_filter = UnivarateSplineAutofitFilter()
    res_autofit = autofit_filter.apply(data_frame_subset)

    # 4. 保存结果
    results = pd.DataFrame()
    results['date_time'] = df['date_time']
    results['Raw_Data'] = df[target_col]
    results['Spline_Fixed_Python'] = res_spline[target_col]
    results['Spline_Auto_Python'] = res_autofit[target_col]

    output_file = "python_spline_result.csv"
    results.to_csv(output_file, index=False)
    print(f"\nSuccess! Spline results saved to: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    generate_spline_truth()