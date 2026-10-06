package com.calopy.maths.gam;

import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.ArrayRealVector;
import org.apache.commons.math3.linear.QRDecomposition;

/**
 * pygam.GAM() 默认设置的单变量版本：s(0) + intercept，正态分布、恒等联系函数。
 *
 * s(0) 是 20 个三次 B 样条（basis='ps'，节点在 [min(x), max(x)] 上等距），
 * 惩罚为 lam = 0.6 乘以系数的二阶差分平方和，截距不惩罚；另外和 pygam 一样在所有系数上
 * 加 sqrt(machine eps) 的岭项。正态 + 恒等时 PIRLS 一步就收敛到惩罚最小二乘解，
 * 这里直接用增广矩阵的 QR 分解求同一个解。
 */
public final class LinearGam {

    private static final double EPS = Math.ulp(1.0);

    private final int nSplines;
    private final int splineOrder;
    private final double lam;

    private double edgeMin;
    private double edgeMax;
    private double[] coef;

    public LinearGam() {
        this(20, 3, 0.6);
    }

    public LinearGam(int nSplines, int splineOrder, double lam) {
        if (nSplines < splineOrder + 1) {
            throw new IllegalArgumentException("nSplines must be >= splineOrder + 1");
        }
        this.nSplines = nSplines;
        this.splineOrder = splineOrder;
        this.lam = lam;
    }

    public LinearGam fit(double[] x, double[] y) {
        int n = x.length;
        edgeMin = Double.POSITIVE_INFINITY;
        edgeMax = Double.NEGATIVE_INFINITY;
        for (double v : x) {
            edgeMin = Math.min(edgeMin, v);
            edgeMax = Math.max(edgeMax, v);
        }
        double[][] basis = basis(x);
        int m = nSplines + 1;
        int nDiff = nSplines - 2;
        double[][] aug = new double[n + nDiff + m][m];
        double[] rhs = new double[n + nDiff + m];
        for (int i = 0; i < n; i++) {
            System.arraycopy(basis[i], 0, aug[i], 0, nSplines);
            aug[i][nSplines] = 1.0;
            rhs[i] = y[i];
        }
        // sqrt(lam) * D2，D2 为二阶差分矩阵；截距列为 0
        double sqrtLam = Math.sqrt(lam);
        for (int r = 0; r < nDiff; r++) {
            aug[n + r][r] = sqrtLam;
            aug[n + r][r + 1] = -2 * sqrtLam;
            aug[n + r][r + 2] = sqrtLam;
        }
        // pygam 的 S = sqrt(eps) * I，其平方根为 eps^(1/4) * I
        double ridge = Math.sqrt(Math.sqrt(EPS));
        for (int j = 0; j < m; j++) {
            aug[n + nDiff + j][j] = ridge;
        }
        coef = new QRDecomposition(new Array2DRowRealMatrix(aug, false))
                .getSolver().solve(new ArrayRealVector(rhs, false)).toArray();
        return this;
    }

    public double[] predict(double[] x) {
        double[][] basis = basis(x);
        double[] out = new double[x.length];
        for (int i = 0; i < x.length; i++) {
            double v = coef[nSplines];
            for (int j = 0; j < nSplines; j++) {
                v += basis[i][j] * coef[j];
            }
            out[i] = v;
        }
        return out;
    }

    /** pygam.utils.b_spline_basis（periodic=False）的逐点版本，递推顺序与原实现相同。 */
    private double[][] basis(double[] x) {
        double offset = edgeMin;
        double scale = edgeMax - edgeMin;
        if (scale == 0) {
            scale = 1;
        }
        int nBoundary = 1 + nSplines - splineOrder;
        double[] boundary = new double[nBoundary];
        // numpy.linspace：第 i 个值为 i * step，最后一个值强制为 stop
        double step = nBoundary == 1 ? 0.0 : 1.0 / (nBoundary - 1);
        for (int i = 0; i < nBoundary; i++) {
            boundary[i] = i * step;
        }
        boundary[nBoundary - 1] = 1.0;
        double diff = boundary[1] - boundary[0];
        double[] knots = new double[nBoundary + 2 * splineOrder];
        for (int i = 0; i < splineOrder; i++) {
            knots[i] = -((splineOrder - i) * diff);
            knots[splineOrder + nBoundary + i] = 1 + (i + 1) * diff;
        }
        System.arraycopy(boundary, 0, knots, splineOrder, nBoundary);
        knots[knots.length - 1] += 1e-9;

        double[][] out = new double[x.length][];
        for (int r = 0; r < x.length; r++) {
            double xi = (x[r] - offset) / scale;
            if (xi < 0 || xi > 1) {
                throw new IllegalArgumentException("prediction outside the fitted range is not supported");
            }
            int maxi = knots.length - 1;
            double[] b = new double[maxi];
            for (int i = 0; i < maxi; i++) {
                b[i] = (xi >= knots[i] && xi < knots[i + 1]) ? 1.0 : 0.0;
            }
            for (int m = 2; m <= splineOrder + 1; m++) {
                maxi--;
                double[] next = new double[maxi];
                for (int i = 0; i < maxi; i++) {
                    double left = (xi - knots[i]) * b[i] / (knots[i + m - 1] - knots[i]);
                    double right = (knots[i + m] - xi) * b[i + 1] / (knots[i + m] - knots[i + 1]);
                    next[i] = left + right;
                }
                b = next;
            }
            out[r] = b;
        }
        return out;
    }
}
