package com.calopy.maths.filter;

import org.junit.jupiter.api.Test;

import static com.calopy.maths.filter.ReferenceData.assertSeriesEquals;
import static com.calopy.maths.filter.ReferenceData.column;
import static com.calopy.maths.filter.ReferenceData.input;

class GeneralizedAdditiveFilterTest {

    private static final double TOL = 1e-8;
    private static final String EXT = "python_extended_result.csv";

    @Test
    void vo2() {
        assertSeriesEquals(column("python_gam_result.csv", "GAM_Python"),
                new GeneralizedAdditiveFilter().apply(input("VO2(3)")), TOL);
    }

    @Test
    void rer() {
        assertSeriesEquals(column(EXT, "RER_GAM"), new GeneralizedAdditiveFilter().apply(input("RER")), TOL);
    }

    @Test
    void missingValues() {
        assertSeriesEquals(column(EXT, "Gap_GAM"),
                new GeneralizedAdditiveFilter().apply(column(EXT, "Gap_Input")), TOL);
    }
}
