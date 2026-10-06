package com.calopy.maths.filter;

import java.util.List;

/**
 * 对应 Calopy 的 RollingWindowGausianFilter：win_type="gaussian"，.mean(std=int(deviation))。
 * Python 端把标准差截断成整数，这里保持一致。
 */
public class RollingWindowGaussianFilter implements CurveFittingFilter {

    public static final String TYPE = "Rolling window - Gaussian";

    private final int window;
    private final int deviation;

    public RollingWindowGaussianFilter(int window, double deviation) {
        if (window <= 0) {
            throw new IllegalArgumentException("window must be > 0");
        }
        if ((int) deviation <= 0) {
            throw new IllegalArgumentException("deviation must be >= 1");
        }
        this.window = window;
        this.deviation = (int) deviation;
    }

    @Override
    public List<Double> apply(List<Double> data) {
        return RollingWindow.weightedMean(data, gaussianWeights(window, deviation));
    }

    /** scipy.signal.windows.gaussian(M, std)。 */
    static double[] gaussianWeights(int m, double std) {
        double[] w = new double[m];
        double sig2 = 2 * std * std;
        for (int i = 0; i < m; i++) {
            double x = i - (m - 1.0) / 2.0;
            w[i] = Math.exp(-(x * x) / sig2);
        }
        return w;
    }

    @Override
    public String getParameterText() {
        return "window:" + window + ",deviation:" + deviation;
    }
}
