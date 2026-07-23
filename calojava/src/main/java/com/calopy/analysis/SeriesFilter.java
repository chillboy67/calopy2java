package com.calopy.analysis;

import java.util.List;

public interface SeriesFilter {
    /**
     * 执行平滑或拟合算法
     * @param inputData 输入的时间序列数据
     * @return 处理后的数据 List
     */
    List<Double> apply(List<Double> inputData);
}