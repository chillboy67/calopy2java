package com.calopy.test;

import com.calopy.maths.filter.*;
import java.nio.file.*;
import java.util.*;
import java.io.*;

public class GamTest {

    public static void main(String[] args) throws Exception {
        String inputCsvPath = "D:\\calopy2java\\example_csv.csv";
        String outputCsvPath = "D:\\calopy2java\\java_gam_result.csv";
        int targetColIndex = 10; // VO2(3)

        // 1. 读取数据
        List<Double> rawData = readCSV(inputCsvPath, targetColIndex);
        System.out.println("读取数据行数: " + rawData.size());

        // 2. 运行 GAM (实际是 Loess)
        System.out.println("运行 GeneralizedAdditiveFilter (Java Loess)...");
        CurveFittingFilter gamFilter = new GeneralizedAdditiveFilter();
        List<Double> resultGam = gamFilter.apply(rawData);

        // 3. 保存结果
        writeResultCSV(outputCsvPath, rawData, resultGam);
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

    private static void writeResultCSV(String filePath, List<Double> raw, List<Double> gam) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath))) {
            writer.println("Index,Raw_Data,GAM_Java_Loess");
            for (int i = 0; i < raw.size(); i++) {
                writer.printf("%d,%s,%s%n",
                        i,
                        raw.get(i) == null ? "" : raw.get(i),
                        gam.get(i) == null ? "" : gam.get(i)
                );
            }
        }
    }
}