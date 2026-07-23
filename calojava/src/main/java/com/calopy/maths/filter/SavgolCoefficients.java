package com.calopy.maths.filter;

public class SavgolCoefficients {

    public static double[] compute(int window, int order) {
        int half = window / 2;
        int rows = window;
        int cols = order + 1;

        double[][] A = new double[rows][cols];

        // 构建 Vandermonde 矩阵
        for (int i = -half; i <= half; i++) {
            for (int j = 0; j <= order; j++) {
                A[i + half][j] = Math.pow(i, j);
            }
        }

        // (A^T A)^-1 A^T
        double[][] AT = transpose(A);
        double[][] ATA = multiply(AT, A);
        double[][] ATAInv = invert(ATA);
        double[][] pseudoInv = multiply(ATAInv, AT);

        // 取第 0 阶导数（平滑）
        double[] coeffs = new double[window];
        for (int i = 0; i < window; i++) {
            coeffs[i] = pseudoInv[0][i];
        }
        return coeffs;
    }

    /* ========= 矩阵工具 ========= */

    private static double[][] transpose(double[][] m) {
        double[][] t = new double[m[0].length][m.length];
        for (int i = 0; i < m.length; i++)
            for (int j = 0; j < m[0].length; j++)
                t[j][i] = m[i][j];
        return t;
    }

    private static double[][] multiply(double[][] a, double[][] b) {
        double[][] r = new double[a.length][b[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < b[0].length; j++)
                for (int k = 0; k < b.length; k++)
                    r[i][j] += a[i][k] * b[k][j];
        return r;
    }

    private static double[][] invert(double[][] m) {
        int n = m.length;
        double[][] a = new double[n][n];
        double[][] inv = new double[n][n];

        for (int i = 0; i < n; i++) {
            inv[i][i] = 1;
            System.arraycopy(m[i], 0, a[i], 0, n);
        }

        for (int i = 0; i < n; i++) {
            double diag = a[i][i];
            for (int j = 0; j < n; j++) {
                a[i][j] /= diag;
                inv[i][j] /= diag;
            }

            for (int k = 0; k < n; k++) {
                if (k == i) continue;
                double factor = a[k][i];
                for (int j = 0; j < n; j++) {
                    a[k][j] -= factor * a[i][j];
                    inv[k][j] -= factor * inv[i][j];
                }
            }
        }
        return inv;
    }
}
