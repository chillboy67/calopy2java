package com.calopy.maths.filter;

import com.calopy.maths.spline.UnivariateSpline;

import java.util.ArrayList;
import java.util.List;

/**
 * 对应 Calopy 的 UnivarateSplineAutofitFilter：在 s = np.arange(0.02, 6, 0.1) 上做网格搜索，
 * 取惩罚平方和 PSS = 残差 + θ·Σ spline''(x)² 最小的 s（θ = 1400），再用该 s 拟合。
 */
public class UnivariateSplineAutofitFilter implements CurveFittingFilter {

    public static final String TYPE = "Univariate spline - autofit";

    private static final double S_START = 0.02;
    private static final double S_END = 6.0;
    private static final double S_STEP = 0.1;
    private static final double THETA = 1400.0;

    @Override
    public List<Double> apply(List<Double> data) {
        double[] y = SeriesValues.toArrayOrNull(data);
        if (y == null) {
            return SeriesValues.allMissing(data.size());
        }
        double[] x = SeriesValues.positions(y.length);
        double[] smoothed = new UnivariateSpline(x, y, findBestS(x, y)).evaluate(x);
        List<Double> result = new ArrayList<>(smoothed.length);
        for (double v : smoothed) {
            result.add(v);
        }
        return result;
    }

    /** grid_find_smoothing_par 的移植，返回已按 round(par, 2) 处理过的 s。 */
    double findBestS(double[] x, double[] y) {
        double[] candidates = arange(S_START, S_END, S_STEP);
        double[] pss = new double[candidates.length];
        int count = 0;
        for (int par = 0; par < candidates.length; par++) {
            pss[par] = penalizedSumOfSquares(x, y, candidates[par]);
            count++;
            // Python 的提前停止：当前这一项之前的连续 3 个 PSS 完全相同
            if (par > 3 && pss[par - 3] == pss[par - 2] && pss[par - 2] == pss[par - 1]) {
                break;
            }
        }
        int best = 0;
        for (int i = 1; i < count; i++) {
            if (pss[i] < pss[best]) {
                best = i;
            }
        }
        return Math.rint(candidates[best] * 100.0) / 100.0;
    }

    private static double penalizedSumOfSquares(double[] x, double[] y, double s) {
        UnivariateSpline spl = new UnivariateSpline(x, y, s);
        double[] d2 = spl.derivative(2).evaluate(x);
        for (int i = 0; i < d2.length; i++) {
            d2[i] = d2[i] * d2[i];
        }
        return spl.getResidual() + THETA * pairwiseSum(d2, 0, d2.length);
    }

    /** numpy.arange 的取值方式：第 i 个值为 start + i * ((start + step) - start)。 */
    private static double[] arange(double start, double stop, double step) {
        int len = (int) Math.ceil((stop - start) / step);
        double[] v = new double[len];
        double delta = (start + step) - start;
        for (int i = 0; i < len; i++) {
            v[i] = i == 1 ? start + step : start + i * delta;
        }
        return v;
    }

    /** numpy.sum 对连续 float64 数组使用的成对求和。 */
    private static double pairwiseSum(double[] a, int from, int n) {
        if (n < 8) {
            double res = 0.0;
            for (int i = 0; i < n; i++) {
                res += a[from + i];
            }
            return res;
        } else if (n <= 128) {
            double[] r = new double[8];
            for (int j = 0; j < 8; j++) {
                r[j] = a[from + j];
            }
            int i;
            for (i = 8; i < n - (n % 8); i += 8) {
                for (int j = 0; j < 8; j++) {
                    r[j] += a[from + i + j];
                }
            }
            double res = ((r[0] + r[1]) + (r[2] + r[3])) + ((r[4] + r[5]) + (r[6] + r[7]));
            for (; i < n; i++) {
                res += a[from + i];
            }
            return res;
        } else {
            int n2 = n / 2;
            n2 -= n2 % 8;
            return pairwiseSum(a, from, n2) + pairwiseSum(a, from + n2, n - n2);
        }
    }

    @Override
    public String getParameterText() {
        return "";
    }
}
