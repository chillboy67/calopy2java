package com.calopy.test;

import com.calopy.maths.filter.*;
import java.nio.file.*;
import java.util.*;
import java.io.*;

public class RollingTest {

    public static void main(String[] args) throws Exception {
        String inputCsvPath = "D:\\calopy2java\\example_csv.csv";
        String outputCsvPath = "D:\\calopy2java\\java_rolling_result.csv";
        int targetColIndex = 10; // VO2(3)

        List<Double> rawData = readCSV(inputCsvPath, targetColIndex);
        System.out.println("读取数据行数: " + rawData.size());

        // 1. 运行 Mean (window=5) --- 新增 ---
        System.out.println("运行 RollingWindowMeanFilter (window=5)...");
        CurveFittingFilter meanFilter = new RollingWindowMeanFilter(5);
        List<Double> resultMean = meanFilter.apply(rawData);

        // 2. 运行 Triangular (window=5)
        System.out.println("运行 RollingWindowTriangularFilter (window=5)...");
        CurveFittingFilter triFilter = new RollingWindowTriangularFilter(5);
        List<Double> resultTri = triFilter.apply(rawData);

        // 3. 运行 Gaussian (window=5, deviation=1.0)
        System.out.println("运行 RollingWindowGaussianFilter (window=5, deviation=1.0)...");
        CurveFittingFilter gaussFilter = new RollingWindowGaussianFilter(5, 1.0);
        List<Double> resultGauss = gaussFilter.apply(rawData);

        // 4. 保存结果 (加入 Mean)
        writeResultCSV(outputCsvPath, rawData, resultMean, resultTri, resultGauss);
        System.out.println("测试完成！结果已保存到: " + outputCsvPath);
    }

    // --- 通用工具方法 ---
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

    // 更新写入方法，接收3个结果列表
    private static void writeResultCSV(String filePath, List<Double> raw,
                                       List<Double> mean, List<Double> tri, List<Double> gauss) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath))) {
            writer.println("Index,Raw_Data,Mean_Java,Triangular_Java,Gaussian_Java");
            for (int i = 0; i < raw.size(); i++) {
                writer.printf("%d,%s,%s,%s,%s%n",
                        i,
                        raw.get(i) == null ? "" : raw.get(i),
                        mean.get(i) == null ? "" : mean.get(i),  // 新增
                        tri.get(i) == null ? "" : tri.get(i),
                        gauss.get(i) == null ? "" : gauss.get(i)
                );
            }
        }
    }
}