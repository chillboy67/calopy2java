package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

public class UnivariateSplineFilter implements CurveFittingFilter {

    public static final String TYPE = "Univariate spline";

    private final double smoothingFactor; // 这对应 Python 的 s (SSE 目标)
    private final CubicSmoothingSpline splineSolver;

    public UnivariateSplineFilter(double smoothingFactor) {
        this.smoothingFactor = smoothingFactor;
        this.splineSolver = new CubicSmoothingSpline();
    }

    @Override
    public List<Double> apply(List<Double> data) {
        System.out.println("UnivariateSpline with target SSE (s): " + smoothingFactor);

        if (data == null || data.size() < 3) {
            return data == null ? new ArrayList<>() : new ArrayList<>(data);
        }

        int n = data.size();
        double[] y = new double[n];
        for (int i = 0; i < n; i++) {
            Double val = data.get(i);
            y[i] = (val != null) ? val : 0.0;
        }

        // [关键修改] 使用 Target Error 模式
        // Python s=10.0 意味着 SSE <= 10.0
        // 我们自动寻找 lambda 使得 SSE ≈ 10.0
        double[] smoothedArr = splineSolver.fitForTargetError(y, smoothingFactor);

        List<Double> result = new ArrayList<>(n);
        for (double v : smoothedArr) {
            result.add(v);
        }
        return result;
    }

    @Override
    public String getParameterText() {
        return "smoothingFactor (s):" + smoothingFactor;
    }
}