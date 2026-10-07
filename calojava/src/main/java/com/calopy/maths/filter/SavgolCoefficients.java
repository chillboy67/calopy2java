package com.calopy.maths.filter;

import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.QRDecomposition;
import org.apache.commons.math3.linear.RealMatrix;

/**
 * 最小二乘多项式的"求值权重"：对 positions 上的数据做 order 阶多项式拟合，
 * 拟合多项式在 evalAt 处的值 = Σ weights[i] * y[i]。
 * Savitzky-Golay 的卷积系数就是 evalAt 取窗口中心时的权重。
 */
final class SavgolCoefficients {

    private SavgolCoefficients() {
    }

    static double[] compute(int window, int order) {
        // 与 scipy.signal.savgol_coeffs 相同：奇数窗口取中心，偶数窗口取 halflen - 0.5
        int half = window / 2;
        double pos = window % 2 == 0 ? half - 0.5 : half;
        return evalWeights(window, order, pos);
    }

    /** positions 为 0..window-1。 */
    static double[] evalWeights(int window, int order, double evalAt) {
        // 以窗口中心为原点、半宽为单位做缩放，保证 Vandermonde 矩阵条件数可控；缩放不改变权重
        double center = (window - 1) / 2.0;
        double scale = Math.max(center, 1.0);
        int cols = order + 1;
        double[][] v = new double[window][cols];
        for (int i = 0; i < window; i++) {
            double u = (i - center) / scale;
            double p = 1.0;
            for (int j = 0; j < cols; j++) {
                v[i][j] = p;
                p *= u;
            }
        }
        double[] e = new double[cols];
        double ue = (evalAt - center) / scale;
        double p = 1.0;
        for (int j = 0; j < cols; j++) {
            e[j] = p;
            p *= ue;
        }

        // weights = V (VᵀV)⁻¹ e = V R⁻¹ R⁻ᵀ e，其中 V = QR
        RealMatrix r = new QRDecomposition(new Array2DRowRealMatrix(v, false)).getR();
        double[] tmp = new double[cols];
        for (int i = 0; i < cols; i++) {
            double s = e[i];
            for (int k = 0; k < i; k++) {
                s -= r.getEntry(k, i) * tmp[k];
            }
            tmp[i] = s / r.getEntry(i, i);
        }
        double[] zz = new double[cols];
        for (int i = cols - 1; i >= 0; i--) {
            double s = tmp[i];
            for (int k = i + 1; k < cols; k++) {
                s -= r.getEntry(i, k) * zz[k];
            }
            zz[i] = s / r.getEntry(i, i);
        }
        double[] weights = new double[window];
        for (int i = 0; i < window; i++) {
            double s = 0.0;
            for (int j = 0; j < cols; j++) {
                s += v[i][j] * zz[j];
            }
            weights[i] = s;
        }
        return weights;
    }
}
