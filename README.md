# calopy2java

A Java 17 port of the signal-processing core of [Calopy](https://calopy.app/), an indirect calorimetry analysis framework. The Python implementation is treated as the reference; the goal of the port is numerical agreement with it, verified column-by-column against committed reference output.

---

## Project Highlights

- **10 filters** ported from Python/NumPy/SciPy to Java 17 (Maven), each cross-validated against the Python implementation on the same 5,256-point input
- **Smoothing rewrite**: the spline smoother was reimplemented as a Whittaker-Eilers penalized least-squares smoother, cutting its disagreement with the Python reference from MAE 9.82 to 0.027 — a 99.7% reduction, roughly 1/365 of the original deviation
- **Banded pentadiagonal solver** written from scratch, so each smoothing solve is O(n) instead of O(n³) dense inversion
- **Automatic λ selection** by binary search, reproducing SciPy's `s` (target-SSE) parameterization rather than requiring a hand-tuned λ
- Reference Python/Shiny app vendored in-tree so both implementations can be run on the same input

---

## Technical Implementation

### The Problem

The first pass of the port produced a spline smoother whose output diverged badly from `scipy.interpolate.UnivariateSpline`: **MAE 9.82** against the Python reference on the `VO2(3)` column, with a Pearson correlation of only **0.787**. On a signal in this range that is not a rounding discrepancy — the two implementations were tracing visibly different curves.

### The Fix: Whittaker-Eilers Smoothing

`CubicSmoothingSpline` replaces knot-based spline fitting with a Whittaker-Eilers smoother, which solves

```
(I + λ · D₂ᵀD₂) z = y
```

for the smoothed series `z`, where `D₂` is the second-difference operator. The implementation consists of:

- A **banded representation** of `I + λ·D₂ᵀD₂`, which is symmetric pentadiagonal (bandwidth 2, not tridiagonal — the second-difference penalty couples each point to its two neighbors on each side)
- A **symmetric pentadiagonal solver** (`solveSymmetricPentadiagonal`) doing banded LU elimination in O(n), avoiding dense inversion
- A **binary search over log₁₀λ ∈ [−15, 15]**, up to 40 iterations with early exit at 5% relative tolerance, targeting a given SSE. This reproduces SciPy's `s` parameter, which constrains the residual sum of squares rather than λ directly.

`UnivariateSplineAutofitFilter` layers the Python autofit sweep on top: a grid search over `s ∈ [0.02, 6.0]` in steps of 0.1, selecting the `s` that minimizes a penalized sum of squares (`SSE + θ·roughness`, θ = 1400).

A global roughness penalty rather than piecewise segment fitting is what accounts for the accuracy difference; knot placement in the original approach was following local noise.

### Cost

Each solve is O(n) and numerically stable across the λ range searched. The autofit path is not cheap in absolute terms — 60 grid points × up to 40 binary-search iterations means up to ~2,400 solves per series. The O(n) scaling is what makes that tractable at n ≈ 5,000.

---

## Filters Implemented

| Filter | Algorithm |
|--------|-----------|
| `CubicSmoothingSpline` | Whittaker-Eilers penalized least squares; banded solver + λ binary search |
| `UnivariateSplineFilter` | Fixed-`s` smoothing spline |
| `UnivariateSplineAutofitFilter` | Grid search over `s`, selected by penalized sum of squares |
| `SavgolFilter` | Savitzky-Golay polynomial smoothing |
| `SingleComponentCosinorFilter` | Cosinor rhythmometry (least squares) |
| `GeneralizedAdditiveFilter` | LOESS local regression (see caveat below) |
| `RollingWindowMeanFilter` | Rolling mean |
| `RollingWindowTriangularFilter` | Triangular-weighted rolling window |
| `RollingWindowGaussianFilter` | Gaussian-weighted rolling window |
| `DoNothingOnSeriesFilter` | Pass-through (baseline) |

---

## Cross-Validation Against the Python Reference

All figures below are Java output vs. Python output on the same input (`example_csv.csv`, column `VO2(3)`, 5,256 points). MAE is the mean absolute difference between the two implementations' smoothed series; `r` is the Pearson correlation between them.

| Filter | MAE vs. Python | r |
|--------|---------------|---|
| Rolling mean | 0.00000 | 1.00000 |
| Rolling triangular | 0.00000 | 1.00000 |
| Rolling Gaussian | 0.00000 | 1.00000 |
| Savitzky-Golay | 0.00071 | 1.00000 |
| Spline (autofit) | 0.02692 | 1.00000 |
| Spline (fixed, s=10) | 0.03524 | 1.00000 |
| Cosinor | 0.98969 | 0.99144 |
| GAM / LOESS | 2.51335 | 0.87656 |

The rolling-window filters are bit-exact. Savitzky-Golay and both spline paths agree to well within the measurement resolution of the underlying signal.

**Two known gaps**, stated plainly because the table above would otherwise be read as uniform success:

- **Cosinor** (MAE 0.99) differs in least-squares conditioning; the fitted rhythm parameters are close but not identical.
- **GAM** (MAE 2.51, r 0.877) is *not* a port. `GeneralizedAdditiveFilter` implements LOESS local regression, whereas the Python side uses a spline-basis GAM. These are different estimators and the numbers reflect that. It is usable as a smoother but should not be treated as reproducing the Python GAM.

### Effect of the smoothing rewrite

`java_spline_result_old.csv` is retained so the change is auditable:

| Column | Before | After |
|--------|--------|-------|
| Spline autofit — MAE vs. Python | 9.8189 | 0.0269 |
| Spline autofit — r vs. Python | 0.78699 | 1.00000 |
| Spline fixed — MAE vs. Python | 7.6583 | 0.0352 |
| Spline fixed — r vs. Python | 0.86981 | 1.00000 |

### Reproducing these numbers

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

## Why Smoothing Error Matters Downstream

Indirect calorimetry produces continuous VO₂ and VCO₂ time series. The quantities actually consumed are derived from them: RER is a ratio (VCO₂/VO₂), and energy expenditure is a linear combination of the two. Both propagate smoothing error rather than average it out.

Two properties of the error matter more than its magnitude:

- **It is systematic, not random.** Knot placement biases the fitted curve in the same direction across neighboring samples, so the error does not cancel when the signal is integrated over a time window or aggregated across subjects.
- **Ratios amplify it near small denominators.** A fixed absolute error in VO₂ produces a relative error in RER scaling as 1/VO₂, so low-VO₂ intervals — resting periods — carry the largest distortion, and those are often the intervals of interest.

This is why the port is validated against reference output rather than against the raw input. Agreement with the raw signal is not a correctness metric for a smoother: a filter that interpolates the noise scores an MAE near zero while doing no smoothing at all. Divergence from a known-good implementation is the property worth measuring.

---

## Repository Structure

```
calopy2java/
├── calopy/                  # Reference Python/Shiny app (MIT, upstream: computational-discovery-research/calopy)
│   └── python_*_result.csv  # Python reference output, used as the comparison baseline
├── calojava/                # Java 17 / Maven port of the signal processing filters
├── example_csv.csv          # Shared input: 5,256-point physiological time series
├── java_*_result.csv        # Java output, compared column-wise against the Python reference
└── java_*_result_old.csv    # Pre-rewrite output, retained for the before/after comparison
```

---

## How to Run

**Python (reference implementation):**
```bash
pip install -r ./calopy/src/requirements.txt
cd ./calopy/src
shiny run --reload --port 8180 --launch-browser ./app.py
```

**Java (calojava):**
```bash
cd calojava
mvn clean package
mvn test
```

> Note: the test harnesses under `calojava/src/test` currently hardcode absolute Windows paths for their input and output CSVs. Adjust those paths before running them on another machine.

---

## Author

**Lukas Alexander**
GitHub: [@chillboy67](https://github.com/chillboy67)

> Reference: Loipfinger S, et al. *Nature Metabolism*, 2025. [DOI: 10.1038/s42255-025-01316-8](https://doi.org/10.1038/s42255-025-01316-8)
> Original Calopy: [https://calopy.app](https://calopy.app/) · MIT License
