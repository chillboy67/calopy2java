package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

public class UnivariateSplineAutofitFilter implements CurveFittingFilter {

    public static final String TYPE = "Univariate spline - autofit";

    // 完全复刻 Python 的参数搜索范围
    // Python: s_start=0.02, s_end=6, s_step=0.1
    private final double sStart = 0.02;
    private final double sEnd = 6.0;
    private final double sStep = 0.1;
    private final double theta = 1400.0;

    private final CubicSmoothingSpline splineSolver = new CubicSmoothingSpline();

    @Override
    public List<Double> apply(List<Double> data) {
        // System.out.println("univariateSplineautofit");
        if (data == null || data.size() < 3) return new ArrayList<>(data);

        int n = data.size();
        double[] y = new double[n];
        for (int i = 0; i < n; i++) {
            Double v = data.get(i);
            y[i] = (v != null) ? v : 0.0;
        }

        // 1. Grid Search Over S (Target SSE)
        // 这次我们搜索的是 SSE 目标，而不是 lambda
        double bestS = findBestS(y);
        System.out.println("Auto-fit found best s (Target SSE): " + bestS);

        // 2. 使用最佳 s 计算最终结果
        double[] smoothedArr = splineSolver.fitForTargetError(y, bestS);

        List<Double> result = new ArrayList<>(n);
        for (double v : smoothedArr) {
            result.add(v);
        }
        return result;
    }

    private double findBestS(double[] y) {
        double bestS = sStart;
        double minPSS = Double.MAX_VALUE;

        // 遍历 Python 定义的 s 范围 (0.02 -> 6.0)
        for (double s = sStart; s <= sEnd; s += sStep) {

            // 关键：对于每一个 s，寻找对应的 fit
            // 如果 s=0.02，这会迫使 Solver 找到极小的 lambda，产生极高精度的拟合
            double[] fitted = splineSolver.fitForTargetError(y, s);

            double pss = computePSS(y, fitted);

            if (pss < minPSS) {
                minPSS = pss;
                bestS = s;
            }
        }
        return bestS;
    }

    private double computePSS(double[] original, double[] fitted) {
        double sse = 0.0;
        int n = original.length;
        for (int i = 0; i < n; i++) {
            double diff = original[i] - fitted[i];
            sse += diff * diff;
        }

        double roughness = 0.0;
        for (int i = 1; i < n - 1; i++) {
            double d2 = fitted[i+1] - 2 * fitted[i] + fitted[i-1];
            roughness += d2 * d2;
        }

        return sse + theta * roughness;
    }

    @Override
    public String getParameterText() {
        return "";
    }
}