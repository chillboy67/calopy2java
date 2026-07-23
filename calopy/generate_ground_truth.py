import pandas as pd
import numpy as np
import os
import sys

# 1. 设置路径 (确保能引用到 calopy 源码)
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from calopy.maths.filter.SavgolFilter import SavgolFilter
#savgol测试
    print("SavgolFilter imported successfully.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


def generate_savgol_truth():
    # 2. 读取文件
    file_path = r"D:\calopy2java\example_csv.csv"
    if not os.path.exists(file_path):
        print(f"Error: 文件未找到: {file_path}")
        return

    print(f"Reading: {file_path}")
    df = pd.read_csv(file_path)

    # 3. 提取 VO2(3) 列
    target_col = 'VO2(3)'
    data_frame_subset = df[[target_col]].copy()

    # 4. 运行 Savgol (参数必须与 Java 测试一致: window=9, order=3)
    print("Running SavgolFilter (window=9, order=3)...")
    savgol_filter = SavgolFilter(window=9, order=3)
    res_savgol = savgol_filter.apply(data_frame_subset)

    # 5. 构造结果 DataFrame
    results = pd.DataFrame()
    results['date_time'] = df['date_time']
    results['Raw_Data'] = df[target_col]
    results['Savgol_Python'] = res_savgol[target_col]

    # 6. 保存到专门的 CSV 文件
    output_file = "python_savgol_result.csv"
    results.to_csv(output_file, index=False)
    print(f"\nSuccess! Savgol ground truth saved to: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    generate_savgol_truth()