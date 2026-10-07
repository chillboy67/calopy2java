package com.calopy.maths.filter;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 重新生成仓库根目录下的 java_*_result.csv（与 calopy/python_*_result.csv 逐列对比用）。
 * 在 calojava/ 下运行：
 * mvn test-compile dependency:build-classpath -Dmdep.outputFile=cp.txt
 * java -cp "target/classes:target/test-classes:$(cat cp.txt)" com.calopy.maths.filter.ExportJavaResults
 */
public final class ExportJavaResults {

    private ExportJavaResults() {
    }

    public static void main(String[] args) throws IOException {
        List<Double> vo2 = ReferenceData.input("VO2(3)");

        Map<String, List<Double>> rolling = new LinkedHashMap<>();
        rolling.put("Mean_Java", new RollingWindowMeanFilter(5).apply(vo2));
        rolling.put("Triangular_Java", new RollingWindowTriangularFilter(5).apply(vo2));
        rolling.put("Gaussian_Java", new RollingWindowGaussianFilter(5, 1.0).apply(vo2));
        write("java_rolling_result.csv", vo2, rolling);

        write("java_savgol_result.csv", vo2, Map.of("Savgol_Java", new SavgolFilter(9, 3).apply(vo2)));
        write("java_cosinor_result.csv", vo2,
                Map.of("Cosinor_Java", new SingleComponentCosinorFilter(144).apply(vo2)));
        write("java_gam_result.csv", vo2, Map.of("GAM_Java", new GeneralizedAdditiveFilter().apply(vo2)));

        Map<String, List<Double>> spline = new LinkedHashMap<>();
        spline.put("Spline_Fixed_Java", new UnivariateSplineFilter(10.0).apply(vo2));
        spline.put("Spline_Auto_Java", new UnivariateSplineAutofitFilter().apply(vo2));
        write("java_spline_result.csv", vo2, spline);
    }

    private static void write(String name, List<Double> raw, Map<String, List<Double>> columns) throws IOException {
        try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(ReferenceData.ROOT.resolve(name)))) {
            w.println("Index,Raw_Data," + String.join(",", columns.keySet()));
            for (int i = 0; i < raw.size(); i++) {
                StringBuilder sb = new StringBuilder().append(i).append(',').append(format(raw.get(i)));
                for (List<Double> col : columns.values()) {
                    sb.append(',').append(format(col.get(i)));
                }
                w.println(sb);
            }
        }
        System.out.println("written " + name);
    }

    private static String format(Double v) {
        return v == null ? "" : v.toString();
    }
}
