package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

/**
 * pandas 的 series.rolling(window, center=True, min_periods=1)（可带权重窗口）：
 * 第 i 个输出取 [i + offset - window + 1, i + offset] 内的数据，offset = (window - 1) / 2，
 * 超出边界或缺失的点跳过，对剩下的点做加权平均；一个有效点都没有时输出缺失。
 */
final class RollingWindow {

    private RollingWindow() {
    }

    static List<Double> weightedMean(List<Double> data, double[] weights) {
        int n = data.size();
        int window = weights.length;
        int offset = (window - 1) / 2;
        List<Double> result = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            int start = i + offset - window + 1;
            double sum = 0.0;
            double weightSum = 0.0;
            int count = 0;
            for (int k = 0; k < window; k++) {
                int idx = start + k;
                if (idx < 0 || idx >= n) {
                    continue;
                }
                Double v = data.get(idx);
                if (SeriesValues.isMissing(v)) {
                    continue;
                }
                sum += v * weights[k];
                weightSum += weights[k];
                count++;
            }
            result.add(count == 0 || weightSum == 0 ? null : sum / weightSum);
        }
        return result;
    }
}
