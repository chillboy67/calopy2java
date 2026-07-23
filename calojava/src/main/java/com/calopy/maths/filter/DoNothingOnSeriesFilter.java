package com.calopy.maths.filter;

import java.util.ArrayList;
import java.util.List;

public class DoNothingOnSeriesFilter implements CurveFittingFilter {

    public static final String TYPE = "Do nothing";

    @Override
    public List<Double> apply(List<Double> data) {
        return new ArrayList<>(data);
    }
}

