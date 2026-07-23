package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

public class RollingWindowTriangularFilter implements CurveFittingFilter {

    private final int window;

    public RollingWindowTriangularFilter(int window) {
        if (window <= 0) {
            throw new IllegalArgumentException("window must be positive");
        }
        this.window = window;
    }

    @Override
    public List<Double> apply(List<Double> data) {
        int n = data.size();
        List<Double> result = new ArrayList<>(n);

        int half = window / 2;
        double[] weights = buildTriangularWeights(window);

        for (int i = 0; i < n; i++) {
            double weightedSum = 0.0;
            double weightSum = 0.0;

            for (int j = -half; j <= half; j++) {
                int idx = i + j;
                if (idx >= 0 && idx < n) {
                    int wIndex = j + half;
                    double w = weights[wIndex];
                    weightedSum += data.get(idx) * w;
                    weightSum += w;
                }
            }

            result.add(weightedSum / weightSum);
        }

        return result;
    }


    private double[] buildTriangularWeights(int window) {
        double[] w = new double[window];
        int mid = window / 2;

        for (int i = 0; i < window; i++) {
            w[i] = mid + 1 - Math.abs(i - mid);
        }
        return w;
    }
}
