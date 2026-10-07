package com.calopy.maths.filter;

import java.util.List;

/** 对应 Calopy 的 RollingWindowTriangularFilter：win_type="triang"（scipy.signal.windows.triang）。 */
public class RollingWindowTriangularFilter implements CurveFittingFilter {

    public static final String TYPE = "Rolling window - triangular";

    private final int window;

    public RollingWindowTriangularFilter(int window) {
        if (window <= 0) {
            throw new IllegalArgumentException("window must be > 0");
        }
        this.window = window;
    }

    @Override
    public List<Double> apply(List<Double> data) {
        return RollingWindow.weightedMean(data, triangularWeights(window));
    }

    static double[] triangularWeights(int m) {
        double[] w = new double[m];
        if (m == 1) {
            w[0] = 1.0;
            return w;
        }
        int half = (m + 1) / 2;
        for (int i = 0; i < half; i++) {
            int k = i + 1;
            double v = m % 2 == 0 ? (2 * k - 1.0) / m : 2 * k / (m + 1.0);
            w[i] = v;
            w[m - 1 - i] = v;
        }
        return w;
    }

    @Override
    public String getParameterText() {
        return "window:" + window;
    }
}
