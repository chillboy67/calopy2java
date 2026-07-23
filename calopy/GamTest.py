import pandas as pd
import numpy as np
import os
import sys

# 1. 引用源码路径
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from calopy.maths.filter.GeneralizedAdditiveFilter import GeneralizedAdditiveFilter

    print("GAM filter imported successfully.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


def generate_gam_truth():
    file_path = r"D:\calopy2java\example_csv.csv"
    if not os.path.exists(file_path):
        print(f"Error: 文件未找到: {file_path}")
        return

    print(f"Reading: {file_path}")
    df = pd.read_csv(file_path)

    target_col = 'VO2(3)'
    data_frame_subset = df[[target_col]].copy()

    # 2. 运行 GAM
    print("Running GeneralizedAdditiveFilter (pygam)...")
    # 注意：这个可能会比其他算法稍微慢一点点
    gam_filter = GeneralizedAdditiveFilter()
    res_gam = gam_filter.apply(data_frame_subset)

    # 3. 保存结果
    results = pd.DataFrame()
    results['date_time'] = df['date_time']
    results['Raw_Data'] = df[target_col]
    results['GAM_Python'] = res_gam[target_col]

    output_file = "python_gam_result.csv"
    results.to_csv(output_file, index=False)
    print(f"\nSuccess! GAM results saved to: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    generate_gam_truth()