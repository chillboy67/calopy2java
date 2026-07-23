# calopy2java

Java port of the [Calopy](https://calopy.app) indirect calorimetry analysis framework, alongside the original Python/Shiny implementation.

## Project Structure

```
calopy2java/
├── calopy/          # Original Python/Shiny app (from GitLab: computational-discovery-research/calopy)
├── calojava/        # Java/Maven port of calopy's core algorithms
├── example_csv.csv  # Example input data
└── java_*_result.csv   # Java output comparison results
```

## calopy — Python

Calopy is an open-source, web-based Shiny for Python application for the intuitive and comprehensive analysis of indirect calorimetry data.

- **Live app:** [https://calopy.app](https://calopy.app)
- **Reference:** Loipfinger S, et al. *Nature Metabolism*, 2025. [DOI: 10.1038/s42255-025-01316-8](https://doi.org/10.1038/s42255-025-01316-8)
- **License:** MIT

### Running calopy locally

```bash
pip install -r ./calopy/src/requirements.txt
cd ./calopy/src
shiny run --reload --port 8180 --launch-browser ./app.py
```

## calojava — Java

A Java 17 / Maven port of calopy's core mathematical filters for indirect calorimetry data processing.

### Implemented Filters

- **SavgolFilter** — Savitzky-Golay smoothing
- **SingleComponentCosinorFilter** — Cosinor rhythmometry
- **GeneralizedAdditiveFilter** — GAM smoothing
- **UnivariateSplineFilter** — Univariate spline
- **UnivariateSplineAutofitFilter** — Auto-fitted spline
- **CubicSmoothingSpline** — Cubic smoothing spline
- **RollingWindowMeanFilter** — Rolling window (mean)
- **RollingWindowGaussianFilter** — Rolling window (Gaussian)
- **RollingWindowTriangularFilter** — Rolling window (triangular)
- **CurveFittingFilter** — Curve fitting

### Building

```bash
cd calojava
mvn clean package
```

### Running Tests

```bash
cd calojava
mvn test
```

## Comparison Results

The root-level CSV files (`java_*_result.csv`) contain outputs comparing the Java implementations against the Python reference outputs (`calopy/python_*_result.csv`), validating the correctness of the Java port.
