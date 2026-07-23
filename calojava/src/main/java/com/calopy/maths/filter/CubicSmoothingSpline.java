package com.calopy.maths.filter;

import java.util.Arrays;

/**
 * 实现 Whittaker-Eilers Smoothing (离散平滑样条) 的核心算法。
 * 包含直接求解器 (Direct Solver) 和 目标误差求解器 (Target Error Solver)。
 */
public class CubicSmoothingSpline {

    /**
     * 核心拟合方法：给定平滑参数 lambda，计算平滑曲线
     * @param y 输入数据
     * @param lambda 平滑参数 (0 = 插值, Infinity = 直线)
     * @return 平滑后的数组
     */
    public double[] fit(double[] y, double lambda) {
        int n = y.length;
        if (n < 3) return Arrays.copyOf(y, n);

        double[] d0 = new double[n];
        double[] d1 = new double[n - 1];
        double[] d2 = new double[n - 2];

        // 构造五对角矩阵系数 (A = I + lambda * D'D)
        for (int i = 0; i < n; i++) {
            double coef;
            if (i == 0 || i == n - 1) coef = 1.0;
            else if (i == 1 || i == n - 2) coef = 5.0;
            else coef = 6.0;
            d0[i] = 1.0 + lambda * coef;
        }

        for (int i = 0; i < n - 1; i++) {
            double coef;
            if (i == 0 || i == n - 2) coef = -2.0;
            else coef = -4.0;
            d1[i] = lambda * coef;
        }

        for (int i = 0; i < n - 2; i++) {
            d2[i] = lambda * 1.0;
        }

        return solveSymmetricPentadiagonal(n, d0, d1, d2, y);
    }

    /**
     * [关键新增] 目标误差拟合：
     * 自动寻找最佳的 lambda，使得平滑后的 SSE (误差平方和) 接近 targetSSE。
     * 这完全模拟了 Python Scipy UnivariateSpline(s=...) 的行为。
     *
     * @param y 输入数据
     * @param targetSSE 目标误差限制 (对应 Python 的 s)
     * @return 符合误差限制的平滑曲线
     */
    public double[] fitForTargetError(double[] y, double targetSSE) {
        // 1. 如果目标误差极大，返回极度平滑（大 lambda）
        // 2. 如果目标误差极小，返回插值（小 lambda）
        // 我们使用二分查找寻找 lambda。由于 SSE(lambda) 是单调递增的，这很有效。

        double lowLog = -15.0; // 1e-15 (接近插值)
        double highLog = 15.0; // 1e15 (接近直线)
        double tolerance = 0.05; // 误差容忍度 5%

        double[] bestFit = null;
        double bestSSEDiff = Double.MAX_VALUE;

        // 二分查找 (30次迭代足以覆盖 double 精度范围)
        for (int i = 0; i < 40; i++) {
            double midLog = (lowLog + highLog) / 2.0;
            double lambda = Math.pow(10, midLog);

            double[] fit = fit(y, lambda);
            double sse = computeSSE(y, fit);

            // 记录最接近的一次
            if (Math.abs(sse - targetSSE) < bestSSEDiff) {
                bestSSEDiff = Math.abs(sse - targetSSE);
                bestFit = fit;
            }

            if (sse < targetSSE) {
                // 误差太小了（曲线太抖），需要更平滑 -> 增大 lambda
                lowLog = midLog;
            } else {
                // 误差太大了（曲线太平），需要更贴合 -> 减小 lambda
                highLog = midLog;
            }

            // 如果已经非常接近目标，提前退出
            if (Math.abs(sse - targetSSE) / (targetSSE + 1e-9) < tolerance) {
                return fit;
            }
        }

        return bestFit;
    }

    private double computeSSE(double[] y, double[] fit) {
        double sse = 0.0;
        for (int i = 0; i < y.length; i++) {
            double d = y[i] - fit[i];
            sse += d * d;
        }
        return sse;
    }

    // 五对角矩阵求解器 (保持不变)
    private double[] solveSymmetricPentadiagonal(int n, double[] d0, double[] d1, double[] d2, double[] b) {
        double[] x = new double[n];
        double[] in = Arrays.copyOf(b, n);
        double[] a = Arrays.copyOf(d0, n);
        double[] u1 = Arrays.copyOf(d1, n - 1);
        double[] u2 = Arrays.copyOf(d2, n - 2);

        for (int i = 0; i < n - 2; i++) {
            if (Math.abs(a[i]) < 1e-12) a[i] = 1e-12;
            double m1 = u1[i] / a[i];
            a[i+1] -= m1 * u1[i];
            u1[i+1] -= m1 * u2[i];
            in[i+1] -= m1 * in[i];

            double m2 = u2[i] / a[i];
            a[i+2] -= m2 * u2[i];
            in[i+2] -= m2 * in[i];
        }

        if (n >= 2) {
            int i = n - 2;
            if (Math.abs(a[i]) < 1e-12) a[i] = 1e-12;
            double m = u1[i] / a[i];
            a[i+1] -= m * u1[i];
            in[i+1] -= m * in[i];
        }

        x[n - 1] = in[n - 1] / a[n - 1];
        if (n >= 2) x[n - 2] = (in[n - 2] - u1[n - 2] * x[n - 1]) / a[n - 2];
        for (int i = n - 3; i >= 0; i--) {
            x[i] = (in[i] - u1[i] * x[i + 1] - u2[i] * x[i + 2]) / a[i];
        }
        return x;
    }
}