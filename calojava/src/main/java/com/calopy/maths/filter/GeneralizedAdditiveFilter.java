package com.calopy.maths.filter;

import com.calopy.maths.gam.LinearGam;

import java.util.ArrayList;
import java.util.List;

/**
 * 对应 Calopy 的 GeneralizedAdditiveFilter：去掉缺失值后，以 0..len-1 为 x 拟合 pygam.GAM()，
 * 预测值放回原来的位置，缺失位置保持缺失。
 */
public class GeneralizedAdditiveFilter implements CurveFittingFilter {

    public static final String TYPE = "Generalized additive model";

    @Override
    public List<Double> apply(List<Double> inputData) {
        List<Integer> originalIndices = new ArrayList<>();
        List<Double> yValues = new ArrayList<>();
        for (int i = 0; i < inputData.size(); i++) {
            Double v = inputData.get(i);
            if (!SeriesValues.isMissing(v)) {
                originalIndices.add(i);
                yValues.add(v);
            }
        }
        List<Double> result = SeriesValues.allMissing(inputData.size());
        if (yValues.isEmpty()) {
            return result;
        }

        // 与 Python 一致：x 是去掉缺失值之后的序号，而不是原始位置
        double[] x = SeriesValues.positions(yValues.size());
        double[] y = new double[yValues.size()];
        for (int i = 0; i < y.length; i++) {
            y[i] = yValues.get(i);
        }
        double[] smoothed = new LinearGam().fit(x, y).predict(x);
        for (int i = 0; i < smoothed.length; i++) {
            result.set(originalIndices.get(i), smoothed[i]);
        }
        return result;
    }

    @Override
    public String getParameterText() {
        return "";
    }
}
