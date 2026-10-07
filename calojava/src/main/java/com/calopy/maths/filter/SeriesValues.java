package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/** 滤波器共用的小工具：缺失值统一用 null 表示（对应 pandas 的 NaN）。 */
final class SeriesValues {

    private SeriesValues() {
    }

    static boolean isMissing(Double v) {
        return v == null || Double.isNaN(v);
    }

    /** 没有缺失值时转成 double[]，否则返回 null。 */
    static double[] toArrayOrNull(List<Double> data) {
        double[] y = new double[data.size()];
        for (int i = 0; i < y.length; i++) {
            Double v = data.get(i);
            if (isMissing(v)) {
                return null;
            }
            y[i] = v;
        }
        return y;
    }

    static double[] positions(int n) {
        double[] x = new double[n];
        for (int i = 0; i < n; i++) {
            x[i] = i;
        }
        return x;
    }

    static List<Double> allMissing(int n) {
        return new ArrayList<>(Collections.nCopies(n, (Double) null));
    }
}
