package com.calopy.maths.filter;

import org.junit.jupiter.api.Test;

import static com.calopy.maths.filter.ReferenceData.assertSeriesEquals;
import static com.calopy.maths.filter.ReferenceData.column;
import static com.calopy.maths.filter.ReferenceData.input;

class SavgolFilterTest {

    private static final double TOL = 1e-9;
    private static final String EXT = "python_extended_result.csv";

    @Test
    void vo2IncludingEdges() {
        assertSeriesEquals(column("python_savgol_result.csv", "Savgol_Python"),
                new SavgolFilter(9, 3).apply(input("VO2(3)")), TOL);
    }

    @Test
    void oddAndEvenWindowOnRer() {
        var rer = input("RER");
        assertSeriesEquals(column(EXT, "RER_Savgol_w9_o3"), new SavgolFilter(9, 3).apply(rer), TOL);
        assertSeriesEquals(column(EXT, "RER_Savgol_w8_o3"), new SavgolFilter(8, 3).apply(rer), TOL);
    }

    @Test
    void missingValues() {
        assertSeriesEquals(column(EXT, "Gap_Savgol_w9_o3"),
                new SavgolFilter(9, 3).apply(column(EXT, "Gap_Input")), TOL);
    }
}
