package com.calopy.maths.filter;

import org.apache.commons.math3.analysis.interpolation.LoessInterpolator;
import org.apache.commons.math3.exception.NoDataException;
import org.apache.commons.math3.exception.NumberIsTooSmallException;

import java.util.ArrayList;
import java.util.List;

public class GeneralizedAdditiveFilter implements CurveFittingFilter {

    @Override
    public List<Double> apply(List<Double> inputData) {
        // 1. 边界检查
        if (inputData == null || inputData.isEmpty()) {
            return new ArrayList<>();
        }

        // 2. 数据清洗 (对应 Python 的 .dropna())
        // 我们需要分离出有效数据(yValues)和它们对应的原始索引(originalIndices)
        List<Double> yValues = new ArrayList<>();
        List<Integer> originalIndices = new ArrayList<>();

        for (int i = 0; i < inputData.size(); i++) {
            Double val = inputData.get(i);
            // 过滤 null 和 NaN
            if (val != null && !Double.isNaN(val)) {
                yValues.add(val);
                originalIndices.add(i);
            }
        }

        // 3. 检查数据量
        // Loess 算法通常至少需要 3 个点才能工作
        if (yValues.size() < 3) {
            // 数据太少无法拟合，直接返回原始数据副本
            return new ArrayList<>(inputData);
        }

        // 4. 准备 Loess 算法所需的数组
        // Python逻辑：xVal = range(0, len(series)) -> 即 0, 1, 2, ...
        double[] x = new double[yValues.size()];
        double[] y = new double[yValues.size()];

        for (int i = 0; i < yValues.size(); i++) {
            x[i] = i; // 仅仅是序号，不是时间戳
            y[i] = yValues.get(i);
        }

        // 5. 执行平滑 (Loess 替代 GAM)
        // bandwidth (带宽): 0.3 (表示每次拟合参考 30% 的邻域数据，类似 GAM 的平滑度)
        // robustnessIters: 2 (鲁棒性迭代次数，用于抵抗异常值)
        LoessInterpolator loess = new LoessInterpolator(0.3, 2);

        double[] smoothedY;
        try {
            smoothedY = loess.smooth(x, y);
        } catch (NumberIsTooSmallException | NoDataException e) {
            System.err.println("Curve fitting failed: " + e.getMessage());
            return new ArrayList<>(inputData); // 失败则回退
        }

        // 6. 结果重组 (Restore to full list)
        // 对应 Python 的 series index 重新对齐
        List<Double> result = new ArrayList<>(inputData.size());

        // 先用 null 填满结果列表
        for (int i = 0; i < inputData.size(); i++) {
            result.add(null);
        }

        // 将计算出的平滑值填回对应的原始位置
        for (int i = 0; i < originalIndices.size(); i++) {
            int originalIndex = originalIndices.get(i);
            result.set(originalIndex, smoothedY[i]);
        }

        return result;
    }

    @Override
    public String getParameterText() {
        return "";
    }
}