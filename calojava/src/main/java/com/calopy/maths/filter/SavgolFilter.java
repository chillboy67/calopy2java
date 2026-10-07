package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

/**
 * 对应 Calopy 的 SavgolFilter：scipy.signal.savgol_filter(y, window, order)，默认 mode='interp'。
 * 中间部分是卷积；首尾各 window/2 个点改为对首/尾 window 个点做多项式拟合后求值。
 * 缺失值和 numpy 的 NaN 一样向外扩散：窗口里有缺失，对应输出就是缺失。
 */
public class SavgolFilter implements CurveFittingFilter {

    public static final String TYPE = "Savitzky-Golay filter";

    private final int window;
    private final int order;
    private final double[] coefficients;

    public SavgolFilter(int window, int order) {
        if (window < 1) {
            throw new IllegalArgumentException("window must be >= 1");
        }
        if (order < 0 || order >= window) {
            throw new IllegalArgumentException("polyorder must be less than window_length.");
        }
        this.window = window;
        this.order = order;
        this.coefficients = SavgolCoefficients.compute(window, order);
    }

    @Override
    public List<Double> apply(List<Double> data) {
        int n = data.size();
        if (window > n) {
            throw new IllegalArgumentException(
                    "If mode is 'interp', window_length must be less than or equal to the size of x.");
        }
        Double[] out = new Double[n];
        int half = window / 2;
        int before = (window - 1) / 2;

        for (int i = half; i < n - half; i++) {
            int start = i - before;
            double sum = 0.0;
            boolean missing = false;
            for (int j = 0; j < window; j++) {
                Double v = data.get(start + j);
                if (SeriesValues.isMissing(v)) {
                    missing = true;
                    break;
                }
                sum += v * coefficients[j];
            }
            out[i] = missing ? null : sum;
        }

        fitEdge(data, 0, 0, half, out);
        fitEdge(data, n - window, n - half, n, out);

        List<Double> result = new ArrayList<>(n);
        for (Double v : out) {
            result.add(v);
        }
        return result;
    }

    /** scipy 的 _fit_edge：用 data[windowStart, windowStart+window) 拟合多项式，填 [from, to) 的输出。 */
    private void fitEdge(List<Double> data, int windowStart, int from, int to, Double[] out) {
        boolean missing = false;
        for (int j = 0; j < window; j++) {
            if (SeriesValues.isMissing(data.get(windowStart + j))) {
                missing = true;
                break;
            }
        }
        for (int i = from; i < to; i++) {
            if (missing) {
                out[i] = null;
                continue;
            }
            double[] w = SavgolCoefficients.evalWeights(window, order, i - windowStart);
            double sum = 0.0;
            for (int j = 0; j < window; j++) {
                sum += data.get(windowStart + j) * w[j];
            }
            out[i] = sum;
        }
    }

    @Override
    public String getParameterText() {
        return "window:" + window + ",order:" + order;
    }
}
