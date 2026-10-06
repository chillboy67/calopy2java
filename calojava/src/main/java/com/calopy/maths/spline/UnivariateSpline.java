package com.calopy.maths.spline;

import java.util.Arrays;

/**
 * 与 scipy.interpolate.UnivariateSpline(x, y, k=3, s=s) 对齐的平滑样条（权重全为 1，区间取 [x[0], x[m-1]]）。
 *
 * 构造流程与 scipy 1.11 相同：先用 nest = max(m/2, 2k+2) 调 fpcurf；如果节点空间不够（ier == 1），
 * 把 nest 扩到 m+k+1，沿用已有节点继续拟合（对应 scipy 的 _reset_nest / fpcurf1）。
 */
public final class UnivariateSpline {

    private static final double TOL = 0.001;
    private static final int MAXIT = 20;

    /** 0 起始的节点和系数，长度都是 n，和 scipy 的 _eval_args = (t[:n], c[:n], k) 一致。 */
    private final double[] t;
    private final double[] c;
    private final int k;
    private final double fp;
    private final int ier;

    public UnivariateSpline(double[] x, double[] y, double s) {
        this(x, y, 3, s);
    }

    public UnivariateSpline(double[] x, double[] y, int k, double s) {
        int m = x.length;
        if (y.length != m) {
            throw new IllegalArgumentException("x and y should have a same length");
        }
        if (k < 1 || k > 5) {
            throw new IllegalArgumentException("k should be 1 <= k <= 5");
        }
        if (!(s >= 0.0)) {
            throw new IllegalArgumentException("s should be s >= 0.0");
        }
        if (m <= k) {
            throw new IllegalArgumentException("need more than k data points");
        }
        for (int i = 1; i < m; i++) {
            if (s > 0 ? !(x[i] - x[i - 1] >= 0.0) : !(x[i] - x[i - 1] > 0.0)) {
                throw new IllegalArgumentException(s > 0 ? "x must be increasing if s > 0"
                        : "x must be strictly increasing if s = 0");
            }
        }

        double[] xf = new double[m + 1];
        double[] yf = new double[m + 1];
        double[] wf = new double[m + 1];
        for (int i = 0; i < m; i++) {
            xf[i + 1] = x[i];
            yf[i + 1] = y[i];
            wf[i + 1] = 1.0;
        }
        double xb = x[0];
        double xe = x[m - 1];

        int k1 = k + 1;
        int nest = s == 0.0 ? m + k + 1 : Math.max(m / 2, 2 * k1);
        Fitpack.Curfit cf = new Fitpack.Curfit(nest);
        Fitpack.fpcurf(0, xf, yf, wf, m, xb, xe, k, s, TOL, MAXIT, cf);
        if (cf.ier == 1) {
            cf.growTo(m + k + 1);
            Fitpack.fpcurf(1, xf, yf, wf, m, xb, xe, k, s, TOL, MAXIT, cf);
        }

        this.k = k;
        this.t = Arrays.copyOfRange(cf.t, 1, cf.n + 1);
        this.c = Arrays.copyOfRange(cf.c, 1, cf.n + 1);
        this.fp = cf.fp;
        this.ier = cf.ier;
    }

    private UnivariateSpline(double[] t, double[] c, int k) {
        this.t = t;
        this.c = c;
        this.k = k;
        this.fp = Double.NaN;
        this.ier = 0;
    }

    /** 在 x 处求值；区间外按多项式外推（scipy 默认 ext=0）。 */
    public double[] evaluate(double[] x) {
        int n = t.length;
        double[] tf = new double[n + 1];
        double[] cf = new double[n + 1];
        System.arraycopy(t, 0, tf, 1, n);
        System.arraycopy(c, 0, cf, 1, n);
        double[] y = new double[x.length];
        Fitpack.splev(tf, n, cf, k, x, y);
        return y;
    }

    /** 对应 scipy 的 splder：返回 nu 阶导数样条。 */
    public UnivariateSpline derivative(int nu) {
        if (nu < 0 || nu > k) {
            throw new IllegalArgumentException("order of derivative must be between 0 and k");
        }
        double[] tt = t;
        double[] cc = c;
        int kk = k;
        for (int j = 0; j < nu; j++) {
            int len = tt.length;
            double[] newC = new double[len - 2];
            for (int i = 0; i < len - 2 - kk; i++) {
                double dt = tt[kk + 1 + i] - tt[1 + i];
                newC[i] = (cc[i + 1] - cc[i]) * kk / dt;
            }
            tt = Arrays.copyOfRange(tt, 1, len - 1);
            cc = newC;
            kk--;
        }
        return new UnivariateSpline(tt, cc, kk);
    }

    /** 残差平方和 fp，对应 scipy 的 get_residual()。 */
    public double getResidual() {
        return fp;
    }

    /** B 样条系数，对应 scipy 的 get_coeffs()。 */
    public double[] getCoeffs() {
        return Arrays.copyOf(c, t.length - k - 1);
    }

    public double[] getKnots() {
        return Arrays.copyOfRange(t, k, t.length - k);
    }

    /** FITPACK 返回码：0 正常，-1 插值样条，-2 最小二乘多项式，1/2/3 为 scipy 会给出警告的情况。 */
    public int getIer() {
        return ier;
    }
}
