package com.calopy.maths.filter;

import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static com.calopy.maths.filter.ReferenceData.assertSeriesEquals;
import static com.calopy.maths.filter.ReferenceData.column;
import static com.calopy.maths.filter.ReferenceData.input;

class UnivariateSplineFiltersTest {

    private static final double TOL = 1e-9;
    private static final String EXT = "python_extended_result.csv";

    @Test
    void fixedSmoothingFactorOnVo2() {
        assertSeriesEquals(column("python_spline_result.csv", "Spline_Fixed_Python"),
                new UnivariateSplineFilter(10.0).apply(input("VO2(3)")), TOL);
    }

    @Test
    void largerSmoothingFactorsOnVo2() {
        var vo2 = input("VO2(3)");
        assertSeriesEquals(column(EXT, "VO2_Spline_s100"), new UnivariateSplineFilter(100.0).apply(vo2), TOL);
        assertSeriesEquals(column(EXT, "VO2_Spline_s500000"), new UnivariateSplineFilter(500000.0).apply(vo2), TOL);
    }

    @Test
    void rerWhereTheSplineActuallySmooths() {
        var rer = input("RER");
        assertSeriesEquals(column(EXT, "RER_Spline_s1"), new UnivariateSplineFilter(1.0).apply(rer), TOL);
        assertSeriesEquals(column(EXT, "RER_Spline_Auto"), new UnivariateSplineAutofitFilter().apply(rer), TOL);
    }

    @Test
    void missingValuesGiveAnAllMissingResultLikeScipy() {
        assertSeriesEquals(column(EXT, "Gap_Spline_s10"),
                new UnivariateSplineFilter(10.0).apply(column(EXT, "Gap_Input")), TOL);
    }

    @Test
    @Tag("slow")
    void autofitOnVo2() {
        assertSeriesEquals(column("python_spline_result.csv", "Spline_Auto_Python"),
                new UnivariateSplineAutofitFilter().apply(input("VO2(3)")), TOL);
    }
}
