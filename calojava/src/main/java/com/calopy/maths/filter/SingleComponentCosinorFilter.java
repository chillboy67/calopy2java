package com.calopy.maths.filter;

import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.ArrayRealVector;
import org.apache.commons.math3.linear.QRDecomposition;
import org.apache.commons.math3.linear.RealVector;

import java.util.ArrayList;
import java.util.List;

/**
 * 对应 Calopy 的 SingleComponentCosinorFilter（CosinorPy.cosinor1.fit_cosinor）：
 * 用普通最小二乘同时拟合 y ~ 1 + cos(2πx/T) + sin(2πx/T)，x 为行号，缺失行不参与拟合（statsmodels 的默认行为），
 * 再由 mesor、amplitude、acrophase 在每一个位置上重建曲线（Calopy 的 fix_series_length）。
 */
public class SingleComponentCosinorFilter implements CurveFittingFilter {

    public static final String TYPE = "Single-component cosinor";

    private final int daylength;

    public SingleComponentCosinorFilter(int daylength) {
        if (daylength <= 0) {
            throw new IllegalArgumentException("daylength must be > 0");
        }
        this.daylength = daylength;
    }

    @Override
    public List<Double> apply(List<Double> data) {
        int n = data.size();
        List<double[]> rows = new ArrayList<>();
        List<Double> values = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            Double v = data.get(i);
            if (SeriesValues.isMissing(v)) {
                continue;
            }
            double angle = 2 * Math.PI * i / daylength;
            rows.add(new double[]{1.0, Math.cos(angle), Math.sin(angle)});
            values.add(v);
        }
        if (rows.size() < 3) {
            return SeriesValues.allMissing(n);
        }

        double[][] design = rows.toArray(new double[0][]);
        double[] y = new double[values.size()];
        for (int i = 0; i < y.length; i++) {
            y[i] = values.get(i);
        }
        RealVector beta = new QRDecomposition(new Array2DRowRealMatrix(design, false))
                .getSolver().solve(new ArrayRealVector(y, false));
        double mesor = beta.getEntry(0);
        double betaR = beta.getEntry(1);
        double betaS = beta.getEntry(2);

        double amplitude = Math.sqrt(betaS * betaS + betaR * betaR);
        double acrophase = projectAcrophase(acrophase(betaS, betaR));

        List<Double> fitted = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            fitted.add(mesor + amplitude * Math.cos((2 * Math.PI * i / daylength) + acrophase));
        }
        return fitted;
    }

    /** CosinorPy.cosinor1.amp_acr（corrected = True）中的象限判断。 */
    private static double acrophase(double sss, double rrr) {
        if (rrr > 0 && sss > 0) {
            return -Math.atan(Math.abs(sss / rrr));
        } else if (rrr > 0 && sss < 0) {
            return -2 * Math.PI + Math.atan(Math.abs(sss / rrr));
        } else if (rrr < 0 && sss > 0) {
            return -Math.PI + Math.atan(Math.abs(sss / rrr));
        } else {
            return -Math.PI - Math.atan(Math.abs(sss / rrr));
        }
    }

    /** CosinorPy.cosinor.project_acr：把相位投影到 [-π, π]（Python 的 % 取余结果与除数同号）。 */
    private static double projectAcrophase(double acr) {
        double period = 2 * Math.PI;
        double mod = acr % period;
        if (mod != 0 && (mod < 0) != (period < 0)) {
            mod += period;
        }
        if (mod > Math.PI) {
            mod -= period;
        } else if (mod < -Math.PI) {
            mod += period;
        }
        return mod;
    }

    @Override
    public String getParameterText() {
        return "daylength:" + daylength;
    }
}
