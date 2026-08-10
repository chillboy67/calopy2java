# calopy2java

[English](./README.md) | **中文**

[Calopy](https://calopy.app/) 间接测热分析框架信号分析核心的 **Java 17 移植**。以 Python 实现为参考基准，目标是在数值上与之对齐，并按列对照已提交的参考输出进行校验。

---

## 项目要点

- **10 种滤波器** 从 Python / NumPy / SciPy 移植到 Java 17（Maven），均在同一组 5,256 点输入上与 Python 实现交叉验证
- **平滑算法重写**：样条平滑改为 Whittaker–Eilers 惩罚最小二乘平滑，与 Python 参考的偏差由 MAE 9.82 降至 0.027，降幅约 99.7%（约为原先偏差的 1/365）
- **带状五对角求解器** 自行实现，单次平滑求解复杂度为 O(n)，避免 O(n³) 稠密矩阵求逆
- **λ 自动选取**：通过二分搜索逼近 SciPy 的 `s`（目标 SSE）参数化方式，无需手工调 λ
- 仓库内附带原版 Python / Shiny 应用，便于在相同输入上对照运行

---

## 技术实现

### 问题

移植第一版的样条平滑与 `scipy.interpolate.UnivariateSpline` 偏差很大：在 `VO2(3)` 列上相对 Python 参考的 **MAE 为 9.82**，Pearson 相关仅 **0.787**。对这一量级的信号而言，已不是舍入误差——两条曲线形状明显不同。

### 方案：Whittaker–Eilers 平滑

`CubicSmoothingSpline` 用 Whittaker–Eilers 平滑替代基于节点的样条拟合，求解：

```
(I + λ · D₂ᵀD₂) z = y
```

其中 `z` 为平滑后序列，`D₂` 为二阶差分算子。实现包括：

- **`I + λ·D₂ᵀD₂` 的带状表示**：对称五对角（带宽为 2，非三对角——二阶差分惩罚使每个点与两侧各两个邻居耦合）
- **对称五对角求解器**（`solveSymmetricPentadiagonal`）：带状 LU 消元，复杂度 O(n)
- **对 log₁₀λ ∈ [−15, 15] 的二分搜索**：最多 40 次迭代，相对容差 5% 时提前退出，以给定 SSE 为目标。对应 SciPy 的 `s` 参数（约束残差平方和，而非直接给 λ）

`UnivariateSplineAutofitFilter` 在其上叠加 Python 侧的 autofit：在 `s ∈ [0.02, 6.0]` 上以 0.1 为步长网格搜索，按惩罚平方和（`SSE + θ·roughness`，θ = 1400）选取最优 `s`。

精度提升主要来自全局粗糙度惩罚，而非分段局部拟合；原先节点放置容易跟着局部噪声走。

### 计算代价

单次求解为 O(n)，在搜索的 λ 范围内数值稳定。autofit 路径绝对开销不小：60 个网格点 × 最多 40 次二分，每条序列最多约 2,400 次求解。在 n ≈ 5,000 时，O(n) 复杂度使这一路径仍可接受。

---

## 已实现的滤波器

| 滤波器 | 算法 |
|--------|------|
| `CubicSmoothingSpline` | Whittaker–Eilers 惩罚最小二乘；带状求解 + λ 二分 |
| `UnivariateSplineFilter` | 固定 `s` 的平滑样条 |
| `UnivariateSplineAutofitFilter` | 对 `s` 网格搜索，按惩罚平方和选取 |
| `SavgolFilter` | Savitzky–Golay 多项式平滑 |
| `SingleComponentCosinorFilter` | Cosinor 节律分析（最小二乘） |
| `GeneralizedAdditiveFilter` | LOESS 局部回归（见下方说明） |
| `RollingWindowMeanFilter` | 滚动均值 |
| `RollingWindowTriangularFilter` | 三角加权滚动窗口 |
| `RollingWindowGaussianFilter` | 高斯加权滚动窗口 |
| `DoNothingOnSeriesFilter` | 直通（基线） |

---

## 相对 Python 参考的交叉验证

下表均为 **Java 输出 vs Python 输出**，同一输入（`example_csv.csv`，列 `VO2(3)`，5,256 点）。MAE 为两条平滑序列的平均绝对差；`r` 为 Pearson 相关系数。

| 滤波器 | 相对 Python 的 MAE | r |
|--------|-------------------|---|
| 滚动均值 | 0.00000 | 1.00000 |
| 滚动三角 | 0.00000 | 1.00000 |
| 滚动高斯 | 0.00000 | 1.00000 |
| Savitzky–Golay | 0.00071 | 1.00000 |
| 样条（autofit） | 0.02692 | 1.00000 |
| 样条（固定，s=10） | 0.03524 | 1.00000 |
| Cosinor | 0.98969 | 0.99144 |
| GAM / LOESS | 2.51335 | 0.87656 |

滚动窗口类滤波器可做到逐点一致。Savitzky–Golay 与两条样条路径的偏差也远小于信号本身的测量分辨量级。

**两处已知差距**（写明是为了避免把上表误读为“全部完全一致”）：

- **Cosinor**（MAE 0.99）：最小二乘条件不同，拟合的节律参数接近但不完全相同。
- **GAM**（MAE 2.51，r 0.877）：**并非** 完整移植。`GeneralizedAdditiveFilter` 实现的是 LOESS，而 Python 侧是样条基 GAM，二者是不同估计器。可用作平滑器，但不应当作 Python GAM 的数值复现。

### 平滑重写前后对比

保留 `java_spline_result_old.csv`，便于审计改动：

| 指标 | 重写前 | 重写后 |
|------|--------|--------|
| 样条 autofit — 相对 Python 的 MAE | 9.8189 | 0.0269 |
| 样条 autofit — 相对 Python 的 r | 0.78699 | 1.00000 |
| 样条 fixed — 相对 Python 的 MAE | 7.6583 | 0.0352 |
| 样条 fixed — 相对 Python 的 r | 0.86981 | 1.00000 |

### 复现上述数字

```python
import csv

def compare(py_file, py_col, java_file, java_col):
    p = [float(r[py_col]) for r in csv.DictReader(open(py_file))]
    j = [float(r[java_col]) for r in csv.DictReader(open(java_file))]
    mae = sum(abs(a - b) for a, b in zip(p, j)) / len(p)
    mp, mj = sum(p) / len(p), sum(j) / len(j)
    num = sum((a - mp) * (b - mj) for a, b in zip(p, j))
    den = (sum((a - mp) ** 2 for a in p) * sum((b - mj) ** 2 for b in j)) ** 0.5
    print(f"MAE={mae:.5f}  r={num / den:.5f}")

compare("calopy/python_spline_result.csv", "Spline_Auto_Python",
        "java_spline_result.csv", "Spline_Auto_Java")
```

---

## 为什么平滑误差会影响下游指标

间接测热得到连续的 VO₂、VCO₂ 时间序列。真正使用的量往往是衍生量：RER 是比值（VCO₂/VO₂），能量消耗是二者的线性组合。两者都会传播平滑误差，而不是把误差“平均掉”。

误差的两个性质比绝对大小更重要：

- **系统性，而非随机。** 节点放置会让邻域样本朝同一方向偏，积分或跨受试者汇总时误差不会相互抵消。
- **比值在分母较小时会放大误差。** VO₂ 上的固定绝对误差，在 RER 上产生的相对误差与 1/VO₂ 成比例，低 VO₂ 区间（如静息）畸变最大，而这往往正是关注区间。

因此移植以参考实现的输出为校验目标，而不是与原始输入比。对平滑器而言，与原始信号的一致并不是正确性指标：一个把噪声也拟合进去的滤波器，MAE 可以接近 0，却几乎没有平滑效果。与已知可靠实现的偏差，才是值得度量的量。

---

## 仓库结构

```
calopy2java/
├── calopy/                  # 参考 Python/Shiny 应用（MIT，上游：computational-discovery-research/calopy）
│   └── python_*_result.csv  # Python 参考输出，作为对照基线
├── calojava/                # Java 17 / Maven 信号滤波器移植
├── example_csv.csv          # 共享输入：5,256 点生理时间序列
├── java_*_result.csv        # Java 输出，按列与 Python 参考对照
└── java_*_result_old.csv    # 重写前输出，用于前后对比
```

---

## 如何运行

**Python（参考实现）：**
```bash
pip install -r ./calopy/src/requirements.txt
cd ./calopy/src
shiny run --reload --port 8180 --launch-browser ./app.py
```

**Java（calojava）：**
```bash
cd calojava
mvn clean package
mvn test
```

> 说明：`calojava/src/test` 下的测试当前写死了 Windows 绝对路径。在其他机器上运行前请先改路径。

---

## 作者

**Lukas Alexander**  
GitHub: [@chillboy67](https://github.com/chillboy67)

> 文献：Loipfinger S, et al. *Nature Metabolism*, 2025. [DOI: 10.1038/s42255-025-01316-8](https://doi.org/10.1038/s42255-025-01316-8)  
> 原版 Calopy：[https://calopy.app](https://calopy.app/) · MIT License
