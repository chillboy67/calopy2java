package com.calopy.maths.filter;

import java.util.Arrays;
import java.util.List;

/** 对应 Calopy 的 RollingWindowMeanFilter：series.rolling(window, center=True, min_periods=1).mean()。 */
public class RollingWindowMeanFilter implements CurveFittingFilter {

    public static final String TYPE = "Rolling window - mean";

    private final int window;

    public RollingWindowMeanFilter(int window) {
        if (window <= 0) {
            throw new IllegalArgumentException("window must be > 0");
        }
        this.window = window;
    }

    @Override
    public List<Double> apply(List<Double> data) {
        double[] weights = new double[window];
        Arrays.fill(weights, 1.0);
        return RollingWindow.weightedMean(data, weights);
    }

    @Override
    public String getParameterText() {
        return "window:" + window;
    }
}
