package com.calopy.test;

import com.calopy.maths.filter.*;
import java.nio.file.*;
import java.util.*;
import java.io.*;

public class CalopyFilterTest {

    public static void main(String[] args) throws Exception {
        // 1. 设置路径
        String inputCsvPath = "D:\\calopy2java\\example_csv.csv";
        String outputCsvPath = "D:\\calopy2java\\java_savgol_result.csv";//savgol测试

        // 2. 读取数据 (注意：要读第 11 列，索引是 10)
        // 第 1 列是 Animal_No (全是1)，第 11 列 VO2(3) 才是波动数据
        int targetColIndex = 10;
        List<Double> rawData = readCSV(inputCsvPath, targetColIndex);
        System.out.println("读取数据行数: " + rawData.size());

        // 3. 运行 Savgol 算法 (参数 window=9, order=3)
        // 这里的参数必须和 Python 生成标准答案时用的参数一致
        System.out.println("正在执行 SavgolFilter (window=9, order=3)...");
        CurveFittingFilter filter = new SavgolFilter(9, 3);
        List<Double> result = filter.apply(rawData);

        // 4. 保存结果到 CSV
        writeResultCSV(outputCsvPath, rawData, result);
        System.out.println("测试完成！结果已保存到: " + outputCsvPath);
    }

    // 读取 CSV
    private static List<Double> readCSV(String filePath, int colIndex) throws IOException {
        List<String> lines = Files.readAllLines(Paths.get(filePath));
        List<Double> result = new ArrayList<>();
        // 跳过 Header
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

    // 写入结果
    private static void writeResultCSV(String filePath, List<Double> raw, List<Double> processed) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath))) {
            writer.println("Index,Raw_Data,Savgol_Java");
            for (int i = 0; i < raw.size(); i++) {
                writer.printf("%d,%s,%s%n",
                        i,
                        raw.get(i) == null ? "" : raw.get(i),
                        processed.get(i) == null ? "" : processed.get(i)
                );
            }
        }
    }
}