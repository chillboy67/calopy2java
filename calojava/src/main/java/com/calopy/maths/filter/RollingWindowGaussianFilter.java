package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

public class RollingWindowGaussianFilter implements CurveFittingFilter {

    private final int window;
    private final double deviation;

    public RollingWindowGaussianFilter(int window, double deviation) {
        if (window <= 0) {
            throw new IllegalArgumentException("window must be > 0");
        }
        if (deviation <= 0) {
            throw new IllegalArgumentException("deviation must be > 0");
        }
        this.window = window;
        this.deviation = deviation;
    }

    @Override
    public List<Double> apply(List<Double> data) {
        int n = data.size();
        List<Double> result = new ArrayList<>(n);

        int halfWindow = window / 2;

        for (int i = 0; i < n; i++) {
            double weightedSum = 0.0;
            double weightTotal = 0.0;

            for (int j = -halfWindow; j <= halfWindow; j++) {
                int idx = i + j;
                if (idx < 0 || idx >= n) {
                    continue;
                }

                double weight = gaussianWeight(j, deviation);
                weightedSum += data.get(idx) * weight;
                weightTotal += weight;
            }

            result.add(weightTotal == 0 ? data.get(i) : weightedSum / weightTotal);
        }

        return result;
    }

    private double gaussianWeight(int x, double sigma) {
        return Math.exp(-(x * x) / (2 * sigma * sigma));
    }
}
