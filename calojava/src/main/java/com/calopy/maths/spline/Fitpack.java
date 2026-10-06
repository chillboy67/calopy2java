package com.calopy.maths.spline;

/**
 * FITPACK (P. Dierckx) 中 scipy.interpolate.UnivariateSpline 用到的子程序的逐行移植：
 * fpcurf / fpknot / fpdisc / fpbspl / fpback / fprati / splev。
 *
 * 为了和 Fortran 源码一一对照，所有数组都按 1 开始编号（下标 0 不用），
 * 变量名、语句顺序和浮点运算顺序都保持与 scipy 1.11 自带的 FITPACK 一致。
 */
final class Fitpack {

    private Fitpack() {
    }

    /** fpcurf 的输入输出状态，对应 f2py 包装 fpcurf0 / fpcurf1 的参数。 */
    static final class Curfit {
        int nest;
        int n;
        double[] t;
        double[] c;
        double fp;
        double[] fpint;
        int[] nrdata;
        int ier;

        Curfit(int nest) {
            this.nest = nest;
            this.t = new double[nest + 1];
            this.c = new double[nest + 1];
            this.fpint = new double[nest + 1];
            this.nrdata = new int[nest + 1];
        }

        /** 对应 scipy 的 _reset_nest：把数组扩到 newNest，保留已有内容。 */
        void growTo(int newNest) {
            t = java.util.Arrays.copyOf(t, newNest + 1);
            c = java.util.Arrays.copyOf(c, newNest + 1);
            fpint = java.util.Arrays.copyOf(fpint, newNest + 1);
            nrdata = java.util.Arrays.copyOf(nrdata, newNest + 1);
            nest = newNest;
        }
    }

    /**
     * fpcurf.f。iopt = 0 从头拟合，iopt = 1 沿用上一次的节点继续（fpcurf1）。
     * x, y, w 均为 1 起始数组，长度 m + 1。
     */
    static void fpcurf(int iopt, double[] x, double[] y, double[] w, int m, double xb, double xe,
                       int k, double s, double tol, int maxit, Curfit cf) {
        final double one = 1.0;
        final double con1 = 0.1;
        final double con9 = 0.9;
        final double con4 = 0.04;
        final double half = 0.5;

        int nest = cf.nest;
        int k1 = k + 1;
        int k2 = k + 2;
        double[] t = cf.t;
        double[] c = cf.c;
        double[] fpint = cf.fpint;
        int[] nrdata = cf.nrdata;
        double[] z = new double[nest + 1];
        double[][] a = new double[nest + 1][k1 + 1];
        double[][] b = new double[nest + 1][k2 + 1];
        double[][] g = new double[nest + 1][k2 + 1];
        double[][] q = new double[m + 1][k1 + 1];
        double[] h = new double[21];
        double[] hh = new double[20];

        int n = cf.n;
        int ier = cf.ier;
        double fp = cf.fp;
        double fp0 = 0.0;
        double fpold = 0.0;
        double fpms = 0.0;
        int nplus = 0;

        int nmin = 2 * k1;
        double acc = tol * s;
        int nmax = m + k1;

        boolean setInterpolationKnots = false;
        if (s > 0.0) {
            // 标号 45 / 50
            boolean restart = true;
            if (iopt != 0 && n != nmin) {
                fp0 = fpint[n];
                fpold = fpint[n - 1];
                nplus = nrdata[n];
                if (fp0 > s) {
                    restart = false;
                }
            }
            if (restart) {
                n = nmin;
                fpold = 0.0;
                nplus = 0;
                nrdata[1] = m - 2;
            }
        } else {
            n = nmax;
            if (nmax > nest) {
                cf.n = n;
                cf.ier = 1;
                return;
            }
            setInterpolationKnots = true;
        }

        boolean smoothingNeeded = false;
        mainLoop:
        while (true) {
            if (setInterpolationKnots) {
                // 标号 10：插值样条的节点就取数据点
                setInterpolationKnots = false;
                int mk1 = m - k1;
                if (mk1 != 0) {
                    int k3 = k / 2;
                    int i = k2;
                    int j = k3 + 2;
                    if (k3 * 2 == k) {
                        for (int l = 1; l <= mk1; l++) {
                            t[i] = (x[j] + x[j - 1]) * half;
                            i++;
                            j++;
                        }
                    } else {
                        for (int l = 1; l <= mk1; l++) {
                            t[i] = x[j];
                            i++;
                            j++;
                        }
                    }
                }
            }

            // 标号 60：在不同的节点集合上反复求最小二乘样条
            iterLoop:
            for (int iter = 1; iter <= m; iter++) {
                if (n == nmin) {
                    ier = -2;
                }
                int nrint = n - nmin + 1;
                int nk1 = n - k1;
                int i = n;
                for (int j = 1; j <= k1; j++) {
                    t[j] = xb;
                    t[i] = xe;
                    i--;
                }
                fp = 0.0;
                for (i = 1; i <= nk1; i++) {
                    z[i] = 0.0;
                    for (int j = 1; j <= k1; j++) {
                        a[i][j] = 0.0;
                    }
                }
                int l = k1;
                for (int it = 1; it <= m; it++) {
                    double xi = x[it];
                    double wi = w[it];
                    double yi = y[it] * wi;
                    while (!(xi < t[l + 1] || l == nk1)) {
                        l++;
                    }
                    fpbspl(t, k, xi, l, h, hh);
                    for (i = 1; i <= k1; i++) {
                        q[it][i] = h[i];
                        h[i] = h[i] * wi;
                    }
                    int j = l - k1;
                    for (i = 1; i <= k1; i++) {
                        j++;
                        double piv = h[i];
                        if (piv == 0.0) {
                            continue;
                        }
                        // fpgivs(piv, a(j,1), cos, sin)
                        double ww = a[j][1];
                        double store = Math.abs(piv);
                        double dd;
                        if (store >= ww) {
                            double r = ww / piv;
                            dd = store * Math.sqrt(one + r * r);
                        } else {
                            double r = piv / ww;
                            dd = ww * Math.sqrt(one + r * r);
                        }
                        double cos = ww / dd;
                        double sin = piv / dd;
                        a[j][1] = dd;
                        // fprota(cos, sin, yi, z(j))
                        double stor1 = yi;
                        double stor2 = z[j];
                        z[j] = cos * stor2 + sin * stor1;
                        yi = cos * stor1 - sin * stor2;
                        if (i == k1) {
                            break;
                        }
                        int i2 = 1;
                        for (int i1 = i + 1; i1 <= k1; i1++) {
                            i2++;
                            stor1 = h[i1];
                            stor2 = a[j][i2];
                            a[j][i2] = cos * stor2 + sin * stor1;
                            h[i1] = cos * stor1 - sin * stor2;
                        }
                    }
                    fp = fp + yi * yi;
                }
                if (ier == -2) {
                    fp0 = fp;
                }
                fpint[n] = fp0;
                fpint[n - 1] = fpold;
                nrdata[n] = nplus;
                fpback(a, z, nk1, k1, c);
                fpms = fp - s;
                if (Math.abs(fpms) < acc) {
                    break mainLoop;
                }
                if (fpms < 0.0) {
                    smoothingNeeded = true;
                    break mainLoop;
                }
                if (n == nmax) {
                    ier = -1;
                    break mainLoop;
                }
                if (n == nest) {
                    ier = 1;
                    break mainLoop;
                }
                if (ier == 0) {
                    // 标号 140：估计这一轮要加多少个节点
                    int npl1 = nplus * 2;
                    double rn = nplus;
                    if (fpold - fp > acc) {
                        npl1 = fortranInt(rn * fpms / (fpold - fp));
                    }
                    nplus = Math.min(nplus * 2, Math.max(Math.max(npl1, nplus / 2), 1));
                } else {
                    nplus = 1;
                    ier = 0;
                }
                // 标号 150：统计每个节点区间的残差平方和
                fpold = fp;
                double fpart = 0.0;
                i = 1;
                l = k2;
                boolean isNew = false;
                for (int it = 1; it <= m; it++) {
                    if (!(x[it] < t[l] || l > nk1)) {
                        isNew = true;
                        l++;
                    }
                    double term = 0.0;
                    int l0 = l - k2;
                    for (int j = 1; j <= k1; j++) {
                        l0++;
                        term = term + c[l0] * q[it][j];
                    }
                    double d = w[it] * (term - y[it]);
                    term = d * d;
                    fpart = fpart + term;
                    if (isNew) {
                        double store = term * half;
                        fpint[i] = fpart - store;
                        i++;
                        fpart = store;
                        isNew = false;
                    }
                }
                fpint[nrint] = fpart;
                for (l = 1; l <= nplus; l++) {
                    fpknot(x, t, n, fpint, nrdata, nrint, 1);
                    n++;
                    nrint++;
                    if (n == nmax) {
                        setInterpolationKnots = true;
                        continue mainLoop;
                    }
                    if (n == nest) {
                        continue iterLoop;
                    }
                }
            }
            smoothingNeeded = true;
            break;
        }

        if (smoothingNeeded && ier != -2) {
            // 标号 250：固定节点，迭代平滑参数 p 使 fp(p) = s
            int nk1 = n - k1;
            fpdisc(t, n, k2, b);
            double p1 = 0.0;
            double f1 = fp0 - s;
            double p3 = -one;
            double f3 = fpms;
            double p = 0.0;
            for (int i = 1; i <= nk1; i++) {
                p = p + a[i][1];
            }
            double rn = nk1;
            p = rn / p;
            int ich1 = 0;
            int ich3 = 0;
            int n8 = n - nmin;
            // 对角元全为正时，h 一旦全为 0，后面的 Givens 旋转都是 cos=1、sin=0 的恒等变换，
            // 可以提前结束内层循环，结果与逐个旋转完全相同。
            boolean diagPositive = true;
            for (int i = 1; i <= nk1; i++) {
                if (!(a[i][1] > 0.0)) {
                    diagPositive = false;
                    break;
                }
            }
            boolean finished = false;
            for (int iter = 1; iter <= maxit; iter++) {
                double pinv = one / p;
                for (int i = 1; i <= nk1; i++) {
                    c[i] = z[i];
                    g[i][k2] = 0.0;
                    for (int j = 1; j <= k1; j++) {
                        g[i][j] = a[i][j];
                    }
                }
                for (int it = 1; it <= n8; it++) {
                    for (int i = 1; i <= k2; i++) {
                        h[i] = b[it][i] * pinv;
                    }
                    double yi = 0.0;
                    for (int j = it; j <= nk1; j++) {
                        double piv = h[1];
                        double ww = g[j][1];
                        double store = Math.abs(piv);
                        double dd;
                        if (store >= ww) {
                            double r = ww / piv;
                            dd = store * Math.sqrt(one + r * r);
                        } else {
                            double r = piv / ww;
                            dd = ww * Math.sqrt(one + r * r);
                        }
                        double cos = ww / dd;
                        double sin = piv / dd;
                        g[j][1] = dd;
                        double stor1 = yi;
                        double stor2 = c[j];
                        c[j] = cos * stor2 + sin * stor1;
                        yi = cos * stor1 - sin * stor2;
                        if (j == nk1) {
                            break;
                        }
                        int i2 = k1;
                        if (j > n8) {
                            i2 = nk1 - j;
                        }
                        for (int i = 1; i <= i2; i++) {
                            int i1 = i + 1;
                            stor1 = h[i1];
                            stor2 = g[j][i1];
                            g[j][i1] = cos * stor2 + sin * stor1;
                            h[i1] = cos * stor1 - sin * stor2;
                            h[i] = h[i1];
                        }
                        h[i2 + 1] = 0.0;
                        if (diagPositive && allZero(h, k2)) {
                            break;
                        }
                    }
                }
                fpback(g, c, nk1, k2, c);
                fp = 0.0;
                int l = k2;
                for (int it = 1; it <= m; it++) {
                    if (!(x[it] < t[l] || l > nk1)) {
                        l++;
                    }
                    int l0 = l - k2;
                    double term = 0.0;
                    for (int j = 1; j <= k1; j++) {
                        l0++;
                        term = term + c[l0] * q[it][j];
                    }
                    double d = w[it] * (term - y[it]);
                    fp = fp + d * d;
                }
                fpms = fp - s;
                if (Math.abs(fpms) < acc) {
                    finished = true;
                    break;
                }
                if (iter == maxit) {
                    break;
                }
                double p2 = p;
                double f2 = fpms;
                if (ich3 == 0) {
                    if (!((f2 - f3) > acc)) {
                        p3 = p2;
                        f3 = f2;
                        p = p * con4;
                        if (p <= p1) {
                            p = p1 * con9 + p2 * con1;
                        }
                        continue;
                    }
                    if (f2 < 0.0) {
                        ich3 = 1;
                    }
                }
                if (ich1 == 0) {
                    if (!((f1 - f2) > acc)) {
                        p1 = p2;
                        f1 = f2;
                        p = p / con4;
                        if (p3 < 0.0) {
                            continue;
                        }
                        if (p >= p3) {
                            p = p2 * con1 + p3 * con9;
                        }
                        continue;
                    }
                    if (f2 > 0.0) {
                        ich1 = 1;
                    }
                }
                if (f2 >= f1 || f2 <= f3) {
                    ier = 2;
                    finished = true;
                    break;
                }
                // fprati：有理插值求下一个 p，同时更新 (p1,f1) 或 (p3,f3)
                double pNew;
                if (p3 > 0.0) {
                    double h1 = f1 * (f2 - f3);
                    double h2 = f2 * (f3 - f1);
                    double h3 = f3 * (f1 - f2);
                    pNew = -(p1 * p2 * h3 + p2 * p3 * h1 + p3 * p1 * h2) / (p1 * h1 + p2 * h2 + p3 * h3);
                } else {
                    pNew = (p1 * (f1 - f3) * f2 - p2 * (f2 - f3) * f1) / ((f1 - f2) * f3);
                }
                if (f2 < 0.0) {
                    p3 = p2;
                    f3 = f2;
                } else {
                    p1 = p2;
                    f1 = f2;
                }
                p = pNew;
            }
            if (!finished) {
                ier = 3;
            }
        }

        cf.n = n;
        cf.fp = fp;
        cf.ier = ier;
    }

    private static boolean allZero(double[] h, int len) {
        for (int i = 1; i <= len; i++) {
            if (h[i] != 0.0) {
                return false;
            }
        }
        return true;
    }

    /** gfortran 在 x86-64 上把超出 int 范围（或 NaN）的 real*8 转 integer 时得到 INT_MIN。 */
    private static int fortranInt(double v) {
        if (Double.isNaN(v) || v >= 2147483648.0 || v <= -2147483649.0) {
            return Integer.MIN_VALUE;
        }
        return (int) v;
    }

    /** fpknot.f：在残差最大的区间中点插入一个新节点。调用方负责 n++、nrint++。 */
    static void fpknot(double[] x, double[] t, int n, double[] fpint, int[] nrdata, int nrint, int istart) {
        int k = (n - nrint - 1) / 2;
        double fpmax = 0.0;
        int jbegin = istart;
        int number = 0;
        int maxpt = 0;
        int maxbeg = 0;
        boolean iserr = true;
        for (int j = 1; j <= nrint; j++) {
            int jpoint = nrdata[j];
            if (!(fpmax >= fpint[j] || jpoint == 0)) {
                iserr = false;
                fpmax = fpint[j];
                number = j;
                maxpt = jpoint;
                maxbeg = jbegin;
            }
            jbegin = jbegin + jpoint + 1;
        }
        if (iserr) {
            return;
        }
        int ihalf = maxpt / 2 + 1;
        int nrx = maxbeg + ihalf;
        int next = number + 1;
        if (next <= nrint) {
            for (int j = next; j <= nrint; j++) {
                int jj = next + nrint - j;
                fpint[jj + 1] = fpint[jj];
                nrdata[jj + 1] = nrdata[jj];
                int jk = jj + k;
                t[jk + 1] = t[jk];
            }
        }
        nrdata[number] = ihalf - 1;
        nrdata[next] = maxpt - ihalf;
        double am = maxpt;
        double an = nrdata[number];
        fpint[number] = fpmax * an / am;
        an = nrdata[next];
        fpint[next] = fpmax * an / am;
        int jk = next + k;
        t[jk] = x[nrx];
    }

    /** fpdisc.f：k 阶导数在内部节点处跳跃量的离散化矩阵。 */
    static void fpdisc(double[] t, int n, int k2, double[][] b) {
        double[] h = new double[13];
        int k1 = k2 - 1;
        int k = k1 - 1;
        int nk1 = n - k1;
        int nrint = nk1 - k;
        double an = nrint;
        double fac = an / (t[nk1 + 1] - t[k1]);
        for (int l = k2; l <= nk1; l++) {
            int lmk = l - k1;
            for (int j = 1; j <= k1; j++) {
                int ik = j + k1;
                int lj = l + j;
                int lk = lj - k2;
                h[j] = t[l] - t[lk];
                h[ik] = t[l] - t[lj];
            }
            int lp = lmk;
            for (int j = 1; j <= k2; j++) {
                int jk = j;
                double prod = h[j];
                for (int i = 1; i <= k; i++) {
                    jk++;
                    prod = prod * h[jk] * fac;
                }
                int lk = lp + k1;
                b[lmk][j] = (t[lk] - t[lp]) / prod;
                lp++;
            }
        }
    }

    /** fpbspl.f：用 de Boor-Cox 递推计算 t(l) <= x < t(l+1) 上 k+1 个非零 B 样条的值。 */
    static void fpbspl(double[] t, int k, double x, int l, double[] h, double[] hh) {
        h[1] = 1.0;
        for (int j = 1; j <= k; j++) {
            for (int i = 1; i <= j; i++) {
                hh[i] = h[i];
            }
            h[1] = 0.0;
            for (int i = 1; i <= j; i++) {
                int li = l + i;
                int lj = li - j;
                if (t[li] != t[lj]) {
                    double f = hh[i] / (t[li] - t[lj]);
                    h[i] = h[i] + f * (t[li] - x);
                    h[i + 1] = f * (x - t[lj]);
                } else {
                    h[i + 1] = 0.0;
                }
            }
        }
    }

    /** fpback.f：带宽为 k 的上三角方程组回代。z 和 c 可以是同一个数组。 */
    static void fpback(double[][] a, double[] z, int n, int k, double[] c) {
        int k1 = k - 1;
        c[n] = z[n] / a[n][1];
        int i = n - 1;
        if (i == 0) {
            return;
        }
        for (int j = 2; j <= n; j++) {
            double store = z[i];
            int i1 = k1;
            if (j <= k1) {
                i1 = j - 1;
            }
            int m = i;
            for (int l = 1; l <= i1; l++) {
                m++;
                store = store - c[m] * a[i][l + 1];
            }
            c[i] = store / a[i][1];
            i--;
        }
    }

    /** splev.f（e = 0，区间外外推）。t、c 为 1 起始数组，x、y 为 0 起始数组。 */
    static void splev(double[] t, int n, double[] c, int k, double[] x, double[] y) {
        double[] h = new double[21];
        double[] hh = new double[20];
        int k1 = k + 1;
        int k2 = k1 + 1;
        int nk1 = n - k1;
        int l = k1;
        int l1 = l + 1;
        for (int i = 0; i < x.length; i++) {
            double arg = x[i];
            while (!(arg >= t[l] || l1 == k2)) {
                l1 = l;
                l = l - 1;
            }
            while (!(arg < t[l1] || l == nk1)) {
                l = l1;
                l1 = l + 1;
            }
            fpbspl(t, k, arg, l, h, hh);
            double sp = 0.0;
            int ll = l - k1;
            for (int j = 1; j <= k1; j++) {
                ll++;
                sp = sp + c[ll] * h[j];
            }
            y[i] = sp;
        }
    }
}
