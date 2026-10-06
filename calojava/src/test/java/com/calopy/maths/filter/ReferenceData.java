package com.calopy.maths.filter;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.fail;

/** 读取仓库根目录下的输入数据和 Python 参考结果（路径相对于 calojava/）。 */
final class ReferenceData {

    static final Path ROOT = Path.of("..");
    static final Path INPUT = ROOT.resolve("example_csv.csv");

    private ReferenceData() {
    }

    static List<Double> column(String file, String name) {
        Path path = file.equals("example_csv.csv") ? INPUT : ROOT.resolve("calopy").resolve(file);
        try {
            List<String> lines = Files.readAllLines(path);
            int idx = Arrays.asList(lines.get(0).split(",", -1)).indexOf(name);
            if (idx < 0) {
                fail("column " + name + " not found in " + path);
            }
            List<Double> values = new ArrayList<>(lines.size() - 1);
            for (int i = 1; i < lines.size(); i++) {
                String line = lines.get(i);
                if (line.isBlank()) {
                    continue;
                }
                String v = line.split(",", -1)[idx].trim();
                values.add(v.isEmpty() || v.equalsIgnoreCase("nan") ? null : Double.parseDouble(v));
            }
            return values;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    static List<Double> input(String name) {
        return column("example_csv.csv", name);
    }

    /** 逐点比较；缺失位置必须一致，其余位置绝对误差不超过 tolerance。 */
    static void assertSeriesEquals(List<Double> expected, List<Double> actual, double tolerance) {
        assertEquals(expected.size(), actual.size(), "length");
        double maxDiff = 0.0;
        int worst = -1;
        for (int i = 0; i < expected.size(); i++) {
            Double e = expected.get(i);
            Double a = actual.get(i);
            if (e == null) {
                assertNull(a, "expected missing value at index " + i);
                continue;
            }
            assertNotNull(a, "unexpected missing value at index " + i);
            double d = Math.abs(e - a);
            if (!(d <= maxDiff)) {
                maxDiff = d;
                worst = i;
            }
        }
        if (!(maxDiff <= tolerance)) {
            fail("max |java - python| = " + maxDiff + " at index " + worst + " (tolerance " + tolerance + ")");
        }
    }
}
