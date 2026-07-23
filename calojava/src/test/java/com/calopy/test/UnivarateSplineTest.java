package com.calopy.test;

import com.calopy.maths.filter.*;
import java.nio.file.*;
import java.util.*;
import java.io.*;

public class UnivarateSplineTest {

    public static void main(String[] args) throws Exception {
        String inputCsvPath = "D:\\calopy2java\\example_csv.csv";
        String outputCsvPath = "D:\\calopy2java\\java_spline_result.csv";
        int targetColIndex = 10; // VO2(3)

        // 1. 读取数据
        List<Double> rawData = readCSV(inputCsvPath, targetColIndex);
        System.out.println("读取数据行数: " + rawData.size());

        // 2. 测试 Univariate Spline (Fixed)
        // Python s=10.0, Java 传入 10.0
        System.out.println("运行 UnivariateSplineFilter (factor=10.0)...");
        CurveFittingFilter fixedFilter = new UnivariateSplineFilter(10.0);
        List<Double> resultFixed = fixedFilter.apply(rawData);

        // 3. 测试 Univariate Spline Autofit
        System.out.println("运行 UnivariateSplineAutofitFilter (可能较慢)...");
        CurveFittingFilter autoFilter = new UnivariateSplineAutofitFilter();
        List<Double> resultAuto = autoFilter.apply(rawData);

        // 4. 保存结果
        writeResultCSV(outputCsvPath, rawData, resultFixed, resultAuto);
        System.out.println("测试完成！结果已保存到: " + outputCsvPath);
    }

    private static List<Double> readCSV(String filePath, int colIndex) throws IOException {
        List<String> lines = Files.readAllLines(Paths.get(filePath));
        List<Double> result = new ArrayList<>();
        for (int i = 1; i < lines.size(); i++) {
            String line = lines.get(i);
            if (line.trim().isEmpty()) continue;
            String[] parts = line.split(",");
            if (parts.length > colIndex) {
                try {
                    String val = parts[colIndex].trim();
                    if (val.isEmpty() || val.equalsIgnoreCase("null")) result.add(null);
                    else result.add(Double.parseDouble(val));
                } catch (NumberFormatException e) { result.add(null); }
            } else { result.add(null); }
        }
        return result;
    }

    private static void writeResultCSV(String filePath, List<Double> raw, List<Double> fixed, List<Double> auto) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath))) {
            writer.println("Index,Raw_Data,Spline_Fixed_Java,Spline_Auto_Java");
            for (int i = 0; i < raw.size(); i++) {
                writer.printf("%d,%s,%s,%s%n",
                        i,
                        raw.get(i) == null ? "" : raw.get(i),
                        fixed.get(i) == null ? "" : fixed.get(i),
                        auto.get(i) == null ? "" : auto.get(i)
                );
            }
        }
    }
}