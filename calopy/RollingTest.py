import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from calopy.maths.filter.RollingWindowMeanFilter import RollingWindowMeanFilter
    from calopy.maths.filter.RollingWindowTriangularFilter import RollingWindowTriangularFilter
    from calopy.maths.filter.RollingWindowGausianFilter import RollingWindowGausianFilter

    print("Rolling Window filters imported successfully.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


def generate_rolling_truth():
    file_path = r"D:\calopy2java\example_csv.csv"
    if not os.path.exists(file_path):
        print(f"Error: 文件未找到: {file_path}")
        return

    print(f"Reading: {file_path}")
    df = pd.read_csv(file_path)

    target_col = 'VO2(3)'
    data_frame_subset = df[[target_col]].copy()

    # 1. 运行 Mean (window=5) --- 新增 ---
    print("Running RollingWindowMeanFilter (window=5)...")
    mean_filter = RollingWindowMeanFilter(5)
    res_mean = mean_filter.apply(data_frame_subset)

    # 2. 运行 Triangular (window=5)
    print("Running RollingWindowTriangularFilter (window=5)...")
    tri_filter = RollingWindowTriangularFilter(5)
    res_tri = tri_filter.apply(data_frame_subset)

    # 3. 运行 Gaussian (window=5, deviation=1.0)
    print("Running RollingWindowGausianFilter (window=5, deviation=1.0)...")
    gauss_filter = RollingWindowGausianFilter(5, 1.0)
    res_gauss = gauss_filter.apply(data_frame_subset)

    # 4. 保存结果
    results = pd.DataFrame()
    results['date_time'] = df['date_time']
    results['Raw_Data'] = df[target_col]
    results['Mean_Python'] = res_mean[target_col]  # 新增列
    results['Triangular_Python'] = res_tri[target_col]
    results['Gaussian_Python'] = res_gauss[target_col]

    output_file = "python_rolling_result.csv"
    results.to_csv(output_file, index=False)
    print(f"\nSuccess! All 3 Rolling results saved to: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    generate_rolling_truth()