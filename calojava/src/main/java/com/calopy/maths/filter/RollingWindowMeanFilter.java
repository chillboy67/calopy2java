package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

public class RollingWindowMeanFilter implements CurveFittingFilter {

    private final int window;
    private final int k;

    public RollingWindowMeanFilter(int window) {
        if (window <= 0 || window % 2 == 0) {
            throw new IllegalArgumentException("window must be a positive odd number");
        }
        this.window = window;
        this.k = (window - 1) / 2;
    }

    @Override
    public List<Double> apply(List<Double> data) {
        List<Double> result = new ArrayList<>(data.size());

        int n = data.size();

        for (int i = 0; i < n; i++) {
            int start = Math.max(0, i - k);
            int end = Math.min(n - 1, i + k);

            double sum = 0.0;
            int count = 0;

            for (int j = start; j <= end; j++) {
                Double value = data.get(j);
                if (value != null) {
                    sum += value;
                    count++;
                }
            }

            result.add(count > 0 ? sum / count : null);
        }

        return result;
    }

    @Override
    public String toString() {
        return "RollingWindowMeanFilter(window=" + window + ")";
    }
}
