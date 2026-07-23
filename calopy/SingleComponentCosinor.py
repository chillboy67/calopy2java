import pandas as pd
import numpy as np
import os
import sys

# 1. 引用源码路径
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from calopy.maths.filter.SingleComponentCosinorFilter import SingleComponentCosinorFilter

    print("Cosinor filter imported successfully.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


def generate_cosinor_truth():
    file_path = r"D:\calopy2java\example_csv.csv"
    if not os.path.exists(file_path):
        print(f"Error: 文件未找到: {file_path}")
        return

    print(f"Reading: {file_path}")
    df = pd.read_csv(file_path)

    target_col = 'VO2(3)'
    data_frame_subset = df[[target_col]].copy()

    # 2. 运行 Cosinor
    # 参数 144 的由来：数据间隔是 10分钟。
    # 1小时 = 6个点，24小时 = 144个点。Cosinor 需要知道一天的周期长度。
    print("Running SingleComponentCosinorFilter (daylength=144)...")
    cosinor = SingleComponentCosinorFilter(144)
    res_cosinor = cosinor.apply(data_frame_subset)

    # 3. 保存结果
    results = pd.DataFrame()
    results['date_time'] = df['date_time']
    results['Raw_Data'] = df[target_col]
    results['Cosinor_Python'] = res_cosinor[target_col]

    output_file = "python_cosinor_result.csv"
    results.to_csv(output_file, index=False)
    print(f"\nSuccess! Cosinor results saved to: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    generate_cosinor_truth()