package com.calopy.maths.filter;

import org.junit.jupiter.api.Test;

import static com.calopy.maths.filter.ReferenceData.assertSeriesEquals;
import static com.calopy.maths.filter.ReferenceData.column;
import static com.calopy.maths.filter.ReferenceData.input;

class RollingWindowFiltersTest {

    private static final double TOL = 1e-9;
    private static final String EXT = "python_extended_result.csv";

    @Test
    void oddWindowOnVo2() {
        var vo2 = input("VO2(3)");
        assertSeriesEquals(column("python_rolling_result.csv", "Mean_Python"),
                new RollingWindowMeanFilter(5).apply(vo2), TOL);
        assertSeriesEquals(column("python_rolling_result.csv", "Triangular_Python"),
                new RollingWindowTriangularFilter(5).apply(vo2), TOL);
        assertSeriesEquals(column("python_rolling_result.csv", "Gaussian_Python"),
                new RollingWindowGaussianFilter(5, 1.0).apply(vo2), TOL);
    }

    @Test
    void evenWindowOnRer() {
        var rer = input("RER");
        assertSeriesEquals(column(EXT, "RER_Mean_w6"), new RollingWindowMeanFilter(6).apply(rer), TOL);
        assertSeriesEquals(column(EXT, "RER_Triangular_w6"), new RollingWindowTriangularFilter(6).apply(rer), TOL);
        assertSeriesEquals(column(EXT, "RER_Gaussian_w6_std2"), new RollingWindowGaussianFilter(6, 2).apply(rer), TOL);
    }

    @Test
    void otherWindowsOnVo2() {
        var vo2 = input("VO2(3)");
        assertSeriesEquals(column(EXT, "VO2_Mean_w4"), new RollingWindowMeanFilter(4).apply(vo2), TOL);
        assertSeriesEquals(column(EXT, "VO2_Triangular_w4"), new RollingWindowTriangularFilter(4).apply(vo2), TOL);
        assertSeriesEquals(column(EXT, "VO2_Gaussian_w10_std3"),
                new RollingWindowGaussianFilter(10, 3).apply(vo2), TOL);
    }

    @Test
    void missingValues() {
        var gap = column(EXT, "Gap_Input");
        assertSeriesEquals(column(EXT, "Gap_Mean_w5"), new RollingWindowMeanFilter(5).apply(gap), TOL);
        assertSeriesEquals(column(EXT, "Gap_Triangular_w5"), new RollingWindowTriangularFilter(5).apply(gap), TOL);
        assertSeriesEquals(column(EXT, "Gap_Gaussian_w5_std1"),
                new RollingWindowGaussianFilter(5, 1).apply(gap), TOL);
    }
}
