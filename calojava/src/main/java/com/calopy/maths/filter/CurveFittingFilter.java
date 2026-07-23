package com.calopy.maths.filter;

import java.util.List;

public interface CurveFittingFilter {
    List<Double> apply(List<Double> data);

    default String getParameterText() {
        return "";
    }
}

