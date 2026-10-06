# calopy2java

[English](./README.md) | **中文**

[Calopy](https://calopy.app/) 间接测热分析框架中**平滑滤波模块**的 Java 17 移植。以 Python 实现为参考基准，用 JUnit 测试逐点对照 Python 的输出。

移植范围只包括 Calopy 平滑页面里的 9 种方法（`calopy/src/calopy/maths/filter`）。数据加载、条件分组、统计、RMR、能量平衡和界面都没有移植。

---

## 项目要点

- **8 种平滑算法加 1 个直通滤波器**，在同一份 5,256 点输入上与 Python 参考的结果一致：滚动窗口和样条**逐位相同**，其余算法的差值在 1e-13 量级。
- **FITPACK 移植**：`scipy.interpolate.UnivariateSpline` 背后的 Dierckx FITPACK 子程序（`fpcurf`、`fpknot`、`fpdisc`、`fpbspl`、`fpback`、`fprati`、`splev`）逐行移植到 Java。节点选择、平滑参数迭代和 scipy 的 nest 扩容流程都和原版相同。
- **pygam GAM 移植**：按 `pygam.GAM()` 默认设置实现：20 个三次 B 样条、二阶差分惩罚（λ = 0.6）、截距项。
- **与 pandas / scipy 的细节行为对齐**：偶数窗口、缺失值、Savitzky–Golay 的 `interp` 边界、高斯标准差截断为整数等。
- **JUnit 5 测试**直接读取 `calopy/python_*.csv` 做断言，使用相对路径。

---

## 已实现的滤波器

| 滤波器 | 对应的 Python 实现 | 说明 |
|--------|-------------------|------|
| `RollingWindowMeanFilter` | `series.rolling(w, center=True, min_periods=1).mean()` | 支持偶数窗口，跳过缺失值 |
| `RollingWindowTriangularFilter` | `win_type="triang"` | 权重同 `scipy.signal.windows.triang` |
| `RollingWindowGaussianFilter` | `win_type="gaussian"`, `std=int(deviation)` | 标准差与 Python 一样截断为整数 |
| `SavgolFilter` | `scipy.signal.savgol_filter(y, w, order)` | 默认 `mode='interp'`：首尾用多项式拟合；支持偶数窗口 |
| `SingleComponentCosinorFilter` | `CosinorPy.cosinor1.fit_cosinor` | 联合最小二乘 `y ~ 1 + cos + sin`，再由 mesor、振幅、相位重建曲线 |
| `GeneralizedAdditiveFilter` | `pygam.GAM()` | P 样条：20 个三次 B 样条 + 二阶差分惩罚 |
| `UnivariateSplineFilter` | `UnivariateSpline(x, y, s)` | FITPACK 移植（`com.calopy.maths.spline`） |
| `UnivariateSplineAutofitFilter` | `UnivarateSplineAutofitFilter` | 在 `np.arange(0.02, 6, 0.1)` 上网格搜索，按 PSS 选 `s` |
| `DoNothingOnSeriesFilter` | `DoNothingOnSeriesFilter` | 原样返回 |

缺失值统一用 `null` 表示，对应 pandas 的 NaN，处理方式与 Python 相同：
- 滚动窗口：跳过缺失值，窗口内没有有效值时输出缺失。
- Savitzky–Golay：缺失值会扩散到包含它的窗口。
- Cosinor：缺失行不参与拟合，但每个位置都会得到拟合值。
- GAM：去掉缺失值后拟合，缺失位置保持缺失。
- 样条：scipy 遇到缺失值时整条结果都是 NaN，Java 版同样整条返回缺失，**不会**把缺失当成 0。

---

## 相对 Python 参考的交叉验证

输入为 `example_csv.csv` 的 `VO2(3)` 列（5,256 点），参数和 `calopy/*.py` 中生成参考结果时一致。表中是 Java 与 Python 输出的平均绝对差（MAE）和最大绝对差。

| 滤波器 | 修复前 MAE | 修复后 MAE | 修复后最大差 |
|--------|-----------|-----------|-------------|
| 滚动均值（w=5） | 0 | 0 | 0 |
| 滚动三角（w=5） | 0 | 0 | 0 |
| 滚动高斯（w=5, std=1） | 0 | 0 | 0 |
| Savitzky–Golay（w=9, order=3） | 0.00071 | 9.9e-14 | 2.3e-13 |
| Cosinor（周期 144） | 0.98969 | 3.7e-14 | 1.7e-13 |
| GAM | 2.51335 | 8.9e-14 | 3.0e-13 |
| 样条（固定，s=10） | 0.03524 | 0 | 0 |
| 样条（autofit） | 0.02692 | 0 | 0 |

`calopy/python_extended_result.csv`（由 `calopy/generate_extended_reference.py` 生成）补充了原有对比覆盖不到的情况。这些用例在测试里都以 1e-9 的容差通过：
- **RER 列**：数值约 0.9，样条在 s=1 时真正起平滑作用。
- **偶数窗口**：Calopy 界面允许的最小窗口是 2。
- **VO2 上更大的 s**：100 和 500,000。
- **含缺失值的输入**。

### 样条的修改经过

1. **第一版**是基于节点的近似实现，与 Python 的 MAE 为 9.82（结果保留在 `java_spline_result_old.csv`）。
2. **第二版**改用 Whittaker–Eilers 离散平滑，在 `VO2(3)`、s=10 上 MAE 降到 0.027。

   但这个参数下 scipy 的样条几乎是插值：Python 输出和原始数据只差 MAE 0.019，直接返回原始数据反而比第二版更接近 Python，所以这个数字不能说明两者一致。换到 RER 列（s=1，真正在平滑）时，第二版与 Python 的差距达到平滑幅度的 43%。
3. **现在**改为逐行移植 FITPACK，所有用例与 scipy 逐位相同。

### 复现上述数字

```python
import csv

def compare(py_file, py_col, java_file, java_col):
    p = [float(r[py_col]) for r in csv.DictReader(open(py_file))]
    j = [float(r[java_col]) for r in csv.DictReader(open(java_file))]
    diffs = [abs(a - b) for a, b in zip(p, j)]
    print(f"MAE={sum(diffs) / len(diffs):.3g}  max={max(diffs):.3g}")

compare("calopy/python_spline_result.csv", "Spline_Auto_Python",
        "java_spline_result.csv", "Spline_Auto_Java")
```

---

## 为什么平滑误差会影响下游指标

间接测热得到的是连续的 VO₂、VCO₂ 时间序列。实际使用的多是衍生量：RER 是比值（VCO₂/VO₂），能量消耗是两者的线性组合。这两种运算都会把平滑误差传下去，而不是平均掉。

- **误差是系统性的。** 相邻样本往同一方向偏，在时间窗口内积分或跨个体汇总时不会相互抵消。
- **比值在分母小时放大误差。** VO₂ 上同样大小的绝对误差，在 RER 上的相对误差与 1/VO₂ 成正比，所以低 VO₂（静息）区间受影响最大，而这些区间往往正是关注的重点。

因此校验对象是参考实现的输出，而不是原始输入。与原始数据接近并不能说明平滑器正确：一个什么都不做的滤波器，和原始数据的 MAE 是 0。

---

## 仓库结构

```
calopy2java/
├── calopy/                           # 参考 Python/Shiny 应用（MIT，上游：computational-discovery-research/calopy）
│   ├── python_*_result.csv           # Python 参考输出
│   ├── python_extended_result.csv    # 扩展用例的 Python 参考输出
│   └── *.py                          # 生成上述参考输出的脚本
├── calojava/                         # Java 17 / Maven 移植
│   ├── src/main/java/com/calopy/maths/filter   # 各滤波器
│   ├── src/main/java/com/calopy/maths/spline   # FITPACK 移植
│   ├── src/main/java/com/calopy/maths/gam      # pygam GAM 移植
│   └── src/test/java                            # JUnit 测试
├── example_csv.csv                   # 共享输入：5,256 点生理时间序列
├── java_*_result.csv                 # Java 输出，按列与 Python 参考对照
└── java_*_result_old.csv             # 早期版本的输出，用于前后对比
```

---

## 如何运行

**Python（参考实现）：**
```bash
pip install -r ./calopy/src/requirements.txt
cd ./calopy/src
shiny run --reload --port 8180 --launch-browser ./app.py
```

重新生成参考结果（任意目录下均可运行）：
```bash
python calopy/generate_extended_reference.py
```

**Java（calojava）：**
```bash
cd calojava
mvn test            # 17 个测试，约 15 秒
mvn test -Pslow     # 另外跑 VO2 上的样条 autofit 对比，约 2 分钟
```

重新生成根目录下的 `java_*_result.csv`：
```bash
cd calojava
mvn test-compile dependency:build-classpath -Dmdep.outputFile=cp.txt
java -cp "target/classes:target/test-classes:$(cat cp.txt)" com.calopy.maths.filter.ExportJavaResults
```

---

## 作者

**Lukas Alexander**  
GitHub: [@chillboy67](https://github.com/chillboy67)

> 文献：Loipfinger S, et al. *Nature Metabolism*, 2025. [DOI: 10.1038/s42255-025-01316-8](https://doi.org/10.1038/s42255-025-01316-8)  
> 原版 Calopy：[https://calopy.app](https://calopy.app/) · MIT License
