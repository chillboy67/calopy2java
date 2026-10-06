package com.calopy.maths.filter;

import org.junit.jupiter.api.Test;

import static com.calopy.maths.filter.ReferenceData.assertSeriesEquals;
import static com.calopy.maths.filter.ReferenceData.column;
import static com.calopy.maths.filter.ReferenceData.input;

class SingleComponentCosinorFilterTest {

    private static final double TOL = 1e-9;
    private static final String EXT = "python_extended_result.csv";

    @Test
    void vo2() {
        assertSeriesEquals(column("python_cosinor_result.csv", "Cosinor_Python"),
                new SingleComponentCosinorFilter(144).apply(input("VO2(3)")), TOL);
    }

    @Test
    void rer() {
        assertSeriesEquals(column(EXT, "RER_Cosinor_144"),
                new SingleComponentCosinorFilter(144).apply(input("RER")), TOL);
    }

    @Test
    void missingRowsAreLeftOutOfTheFitButStillGetAValue() {
        assertSeriesEquals(column(EXT, "Gap_Cosinor_144"),
                new SingleComponentCosinorFilter(144).apply(column(EXT, "Gap_Input")), TOL);
    }
}
