package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

public class SavgolFilter implements CurveFittingFilter {

    public static final String TYPE = "Savitzky-Golay filter";

    private final int window;
    private final int order;
    private final double[] coefficients;

    public SavgolFilter(int window, int order) {
        if (window % 2 == 0) {
            throw new IllegalArgumentException("window must be odd");
        }
        if (order >= window) {
            throw new IllegalArgumentException("order must be < window");
        }
        this.window = window;
        this.order = order;
        this.coefficients = SavgolCoefficients.compute(window, order);
    }

    @Override
    public List<Double> apply(List<Double> data) {
        int n = data.size();
        int half = window / 2;
        List<Double> result = new ArrayList<>(n);

        for (int i = 0; i < n; i++) {
            double sum = 0.0;

            for (int j = -half; j <= half; j++) {
                int idx = i + j;

                // 边界处理：mirror（比直接 clamp 平滑）
                if (idx < 0) idx = -idx;
                if (idx >= n) idx = 2 * n - idx - 2;

                sum += data.get(idx) * coefficients[j + half];
            }
            result.add(sum);
        }

        return result;
    }

    public String getParameterText() {
        return "window:" + window + ",order:" + order;
    }
}
