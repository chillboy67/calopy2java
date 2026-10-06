package com.calopy.maths.filter;

import com.calopy.maths.spline.UnivariateSpline;

import java.util.ArrayList;
import java.util.List;

/**
 * 对应 Calopy 的 UnivariateSplineFilter：scipy.interpolate.UnivariateSpline(range(n), y, s=smoothingFactor)。
 */
public class UnivariateSplineFilter implements CurveFittingFilter {

    public static final String TYPE = "Univariate spline";

    private final double smoothingFactor;

    public UnivariateSplineFilter(double smoothingFactor) {
        this.smoothingFactor = smoothingFactor;
    }

    @Override
    public List<Double> apply(List<Double> data) {
        double[] y = SeriesValues.toArrayOrNull(data);
        if (y == null) {
            // scipy 遇到缺失值时整条结果都是 NaN，这里同样整条返回缺失
            return SeriesValues.allMissing(data.size());
        }
        double[] x = SeriesValues.positions(y.length);
        double[] smoothed = new UnivariateSpline(x, y, smoothingFactor).evaluate(x);
        List<Double> result = new ArrayList<>(smoothed.length);
        for (double v : smoothed) {
            result.add(v);
        }
        return result;
    }

    @Override
    public String getParameterText() {
        return "smoothingfactor:" + smoothingFactor;
    }
}
