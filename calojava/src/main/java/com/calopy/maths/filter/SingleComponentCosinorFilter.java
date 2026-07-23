package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

public class SingleComponentCosinorFilter implements CurveFittingFilter {

    public static final String TYPE = "Single-component cosinor";

    private final int daylength;

    public SingleComponentCosinorFilter(int daylength) {
        this.daylength = daylength;
    }

    @Override
    public List<Double> apply(List<Double> data) {
        int n = data.size();

        double[] cos = new double[n];
        double[] sin = new double[n];

        for (int i = 0; i < n; i++) {
            double angle = 2.0 * Math.PI * i / daylength;
            cos[i] = Math.cos(angle);
            sin[i] = Math.sin(angle);
        }

        double sumY = 0, sumCos = 0, sumSin = 0;
        double sumYCos = 0, sumYSin = 0;
        double sumCos2 = 0, sumSin2 = 0;

        for (int i = 0; i < n; i++) {
            double y = data.get(i);
            sumY += y;
            sumCos += cos[i];
            sumSin += sin[i];
            sumYCos += y * cos[i];
            sumYSin += y * sin[i];
            sumCos2 += cos[i] * cos[i];
            sumSin2 += sin[i] * sin[i];
        }

        double mesor = sumY / n;

        double betaCos = sumYCos / sumCos2;
        double betaSin = sumYSin / sumSin2;

        double amplitude = Math.sqrt(betaCos * betaCos + betaSin * betaSin);
        double phase = Math.atan2(-betaSin, betaCos);

        List<Double> fitted = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            double value = mesor +
                    amplitude * Math.cos((2.0 * Math.PI * i / daylength) + phase);
            fitted.add(value);
        }

        return fitted;
    }

    @Override
    public String getParameterText() {
        return "daylength:" + daylength;
    }
}
