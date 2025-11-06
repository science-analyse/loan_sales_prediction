"""
Forecast pipeline for 'Nağd_pul_kredit_satışı' (quarterly) — robust classical approach for very short series.

How to run:
    1) Ensure the file path notebooks/data/ml_ready_data.csv exists and contains your data
       with the column 'Nağd_pul_kredit_satışı' and the quarter column 'Rüblər' using format like "2020 I", "2020 II", etc.
    2) Install dependencies if needed:
       pip install pandas numpy statsmodels scipy tqdm
    3) Run this script (python forecast_pipeline.py)

Outputs (in the running directory):
    - model_comparison.csv : per-model cross-validated errors (sMAPE, MASE)
    - forecasts_full_fit.csv : final model forecasts for the next n_periods (default 1)
    - model_diagnostics.txt : short diagnostics summary printed to stdout and saved
"""

#     https://www.mdpi.com/2073-8994/14/6/1231

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from datetime import datetime
import os
import math
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import STL
import statsmodels.api as sm
from tqdm import tqdm

# -------------------------
# Configuration / Settings
# -------------------------
DATA_PATH = "data/ml_ready_data.csv"   # <-- as requested
TIME_COL = "Rüblər"                              # quarter column like "2020 I"
TARGET_COL = "Nağd_pul_kredit_satışı"            # target variable to forecast
FREQ = "Q"                                       # quarterly
SEASONAL_PERIODS = 4                             # quarterly seasonality
FORECAST_HORIZON = 2                              # 2-step ahead forecast (2025 Q3 and Q4)
MIN_TRAIN_SPLITS = 8                              # minimum training size for rolling CV (adjustable)
N_CV_FOLDS = None                                 # if None use rolling until last-FORECAST_HORIZON
SARIMA_MAX_P = 2
SARIMA_MAX_Q = 2
SARIMA_D_VALUES = [0, 1]
SARIMA_P_VALUES = list(range(0, SARIMA_MAX_P + 1))
SARIMA_Q_VALUES = list(range(0, SARIMA_MAX_Q + 1))
SARIMA_P_SEASONAL = [0, 1]
SARIMA_Q_SEASONAL = [0, 1]
SARIMA_D_SEASONAL = [0, 1]
SEED = 2025

np.random.seed(SEED)

# -------------------------
# Utility functions
# -------------------------
def parse_quarter_to_period(qstr):
    """
    Parse quarter strings like '2020 I' or '2020 II ' (note possible trailing spaces)
    and return a pandas Period('YYYYQn') or Timestamp for use as index.
    """
    if pd.isna(qstr):
        return None
    s = str(qstr).strip()
    # Standardize roman numerals to integer quarter
    # Handle both "2020 I" and "2020 I," type variants
    parts = s.split()
    if len(parts) < 2:
        # fallback: try to interpret as yyyy-mm
        try:
            return pd.Period(s)
        except Exception:
            return None
    year = parts[0]
    qpart = parts[1].upper()
    map_q = {"I": 1, "II": 2, "III": 3, "IV": 4, "1": 1, "2": 2, "3": 3, "4": 4}
    qnum = map_q.get(qpart.strip(), None)
    if qnum is None:
        # sometimes there is 'I,' or 'II,' -> strip punctuation
        qpart2 = ''.join(ch for ch in qpart if ch.isalnum())
        qnum = map_q.get(qpart2, None)
    if qnum is None:
        return None
    try:
        p = pd.Period(f"{int(year)}Q{qnum}", freq='Q')
        return p
    except Exception:
        return None

def smape(true, pred):
    """Symmetric Mean Absolute Percentage Error (as fraction, not percent)"""
    true = np.asarray(true, dtype=float).flatten()
    pred = np.asarray(pred, dtype=float).flatten()

    # Check for NaN or inf values
    if np.any(~np.isfinite(true)) or np.any(~np.isfinite(pred)):
        return np.nan

    denom = (np.abs(true) + np.abs(pred))
    # avoid division by zero
    mask = denom == 0
    if np.all(mask):
        return 0.0
    denom[mask] = 1.0
    result = np.abs(true - pred) / denom
    result = result[~mask]  # only include non-zero denominators

    if len(result) == 0:
        return np.nan

    return 2.0 * np.mean(result)

def mase(training_series, true, pred):
    """
    Mean Absolute Scaled Error (MASE)
    training_series: 1d array used for scaling (in-sample training)
    true, pred: arrays of same length for forecast period
    """
    true = np.asarray(true, dtype=float).flatten()
    pred = np.asarray(pred, dtype=float).flatten()

    # Check for NaN or inf values
    if np.any(~np.isfinite(true)) or np.any(~np.isfinite(pred)):
        return np.nan

    n = len(training_series)
    if n < 2:
        return np.nan
    # naive one-step training errors
    denom = np.mean(np.abs(np.diff(training_series)))
    if denom == 0 or not np.isfinite(denom):
        return np.nan
    mae = np.mean(np.abs(true - pred))
    if not np.isfinite(mae):
        return np.nan
    return mae / denom

def create_fourier_terms(n_obs, period, K):
    """
    Create Fourier terms design matrix for given series length.
    n_obs: length of series (int)
    period: seasonal period (int)
    K: number of harmonics (1..floor(period/2))
    returns: n_obs x (2*K) numpy array with columns [sin(2*pi*k*t/period), cos(...)] for k=1..K
    """
    t = np.arange(1, n_obs + 1)
    result = []
    for k in range(1, K+1):
        result.append(np.sin(2 * np.pi * k * t / period))
        result.append(np.cos(2 * np.pi * k * t / period))
    if len(result) == 0:
        return np.zeros((n_obs, 0))
    return np.column_stack(result)

# -------------------------
# Read & prepare data
# -------------------------
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Data file not found at {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# Parse quarter column to a Period index
df['_PERIOD'] = df[TIME_COL].apply(parse_quarter_to_period)
if df['_PERIOD'].isnull().any():
    # warn but continue
    missing = df[df['_PERIOD'].isnull()]
    print("Warning: Some 'Rüblər' (quarter) rows could not be parsed and will be dropped:", missing.index.tolist())

df = df.dropna(subset=['_PERIOD']).copy()
df = df.sort_values('_PERIOD').reset_index(drop=True)

# convert to timestamp index (use period.to_timestamp() to set a standard date)
df['_TS'] = df['_PERIOD'].apply(lambda p: p.to_timestamp())
df.set_index('_TS', inplace=True)

# Ensure target is numeric
df[TARGET_COL] = pd.to_numeric(df[TARGET_COL], errors='coerce')

# For training, drop final row(s) where target is missing (we forecast these)
df_obs = df.dropna(subset=[TARGET_COL]).copy()

if df_obs.shape[0] < 8:
    print("Warning: fewer than 8 observations with non-missing target. Results will be fragile.")

series = df_obs[TARGET_COL].astype(float)
series.name = TARGET_COL

# Set explicit quarterly frequency to avoid warnings - use infer_freq to get the right anchor
try:
    inferred_freq = pd.infer_freq(series.index)
    if inferred_freq and inferred_freq.startswith('Q'):
        series.index.freq = inferred_freq
    else:
        # Fallback: manually set to QS (quarter start)
        series.index.freq = 'QS'
except:
    # If inference fails, just continue without setting freq
    pass

print("Series covers from", series.index[0].date(), "to", series.index[-1].date(), "| Observations:", len(series))

# -------------------------
# Forecasting method implementations
# -------------------------
def seasonal_naive_forecast(train_series, h=1, seasonal_periods=4):
    """
    seasonal naive: forecast for horizon h is value at time t - seasonal_periods
    if not available (short train), fallback to last observed value
    """
    if len(train_series) >= seasonal_periods:
        last_same_season = train_series.iloc[-seasonal_periods]
        return np.repeat(last_same_season, h)
    else:
        return np.repeat(train_series.iloc[-1], h)

def sma_forecast(train_series, h=1, window=4):
    """simple moving average of last 'window' observations"""
    if len(train_series) >= window:
        val = train_series.iloc[-window:].mean()
    else:
        val = train_series.mean()
    return np.repeat(val, h)

def ets_forecast(train_series, h=1, seasonal_periods=4):
    """
    ETS forecast using statsmodels' ExponentialSmoothing
    returns forecast array (length h). Fail-safe: if fitting fails return last observed.
    """
    try:
        # Use additive trend + additive seasonal as default for short-sample approach.
        model = ExponentialSmoothing(train_series, trend='add', seasonal='add',
                                     seasonal_periods=seasonal_periods, initialization_method="estimated")
        fit = model.fit(optimized=True)
        fc = fit.forecast(h)
        return np.asarray(fc)
    except Exception as ex:
        # fallback to last value
        return np.repeat(train_series.iloc[-1], h)

def sarima_grid_search_forecast(train_series, h=1, seasonal_periods=4,
                                p_values=[0,1], d_values=[0,1], q_values=[0,1],
                                P_values=[0,1], D_values=[0,1], Q_values=[0,1],
                                maxiter=200, method='lbfgs'):
    """
    Robust SARIMA grid search:
      - uses safer optimizer settings (maxiter, method) to improve convergence chances
      - skips models that raise numerical exceptions
      - logs failed combos in 'failed_models' (returned)
    Returns:
      (forecast_array, best_result_object_or_None, best_order_tuple_or_None, failed_models_list)
    """
    best_aic = np.inf
    best_res = None
    best_order = None
    failed_models = []

    for p in p_values:
        for d in d_values:
            for q in q_values:
                for P in P_values:
                    for D in D_values:
                        for Q in Q_values:
                            try:
                                mod = sm.tsa.statespace.SARIMAX(train_series,
                                                                order=(p,d,q),
                                                                seasonal_order=(P,D,Q,seasonal_periods),
                                                                enforce_stationarity=False,
                                                                enforce_invertibility=False)
                                # Use try/except around fit and limit iterations
                                res = mod.fit(disp=False, method=method, maxiter=maxiter)
                                # check convergence info in mle_retvals if present
                                if hasattr(res, 'mle_retvals'):
                                    mr = res.mle_retvals
                                    # If solver reports failure, skip
                                    if isinstance(mr, dict) and mr.get('warnflag', 0) != 0:
                                        failed_models.append(((p,d,q),(P,D,Q,seasonal_periods), "solver_warnflag", mr))
                                        continue
                                # fallback to res.mle_retvals not present -> rely on res.mle_retvals if available
                                if not np.isfinite(res.aic):
                                    failed_models.append(((p,d,q),(P,D,Q,seasonal_periods), "nonfinite_aic", None))
                                    continue

                                if res.aic < best_aic:
                                    best_aic = res.aic
                                    best_res = res
                                    best_order = ((p,d,q),(P,D,Q,seasonal_periods))
                            except Exception as exc:
                                # record failure: numeric or convergence
                                failed_models.append(((p,d,q),(P,D,Q,seasonal_periods), repr(exc)))
                                continue

    if best_res is not None:
        try:
            pred = best_res.get_forecast(steps=h)
            return np.asarray(pred.predicted_mean), best_res, best_order, failed_models
        except Exception as e:
            return np.repeat(train_series.iloc[-1], h), None, None, failed_models
    else:
        return np.repeat(train_series.iloc[-1], h), None, None, failed_models


def stl_deseasonalize_arima_forecast(train_series, h=1, seasonal_periods=4, arima_order=None):
    """
    STL decomposition -> forecast deseasonalized series with small ARIMA (grid search),
    then add back seasonality forecast (seasonal naive of last seasonal cycle).
    """
    n = len(train_series)
    # Apply STL with period=seasonal_periods and robust=True
    try:
        stl = STL(train_series, period=seasonal_periods, robust=True)
        res = stl.fit()
        seasonal = res.seasonal
        resid = res.trend + res.resid  # deseasonalized (trend+remainder)
    except Exception:
        # if STL fails, fallback to train_series and no deseasonalization
        seasonal = pd.Series(np.zeros(n), index=train_series.index)
        resid = train_series.copy()

    # Forecast the deseasonalized series with small ARIMA search (we call sarima_grid_search_forecast on resid)
    fc_resid, fitted_model, fitted_order, _ = sarima_grid_search_forecast(resid, h=h,
                                                                       seasonal_periods=seasonal_periods,
                                                                       p_values=SARIMA_P_VALUES,
                                                                       d_values=SARIMA_D_VALUES,
                                                                       q_values=SARIMA_Q_VALUES,
                                                                       P_values=[0], D_values=[0], Q_values=[0])
    # Seasonality forecast: repeat last seasonal pattern forward (seasonal-naive)
    last_seasonal = seasonal.iloc[-seasonal_periods:]
    seasonal_fc = np.tile(last_seasonal.values, math.ceil(h / seasonal_periods))[:h]

    final_fc = fc_resid + seasonal_fc
    return final_fc, fitted_model, fitted_order

# -------------------------
# Rolling-origin cross-validation
# -------------------------
def rolling_origin_evaluation(series, h=1, min_train=8):
    """
    Rolling-origin evaluation for a list of model functions.
    Returns a DataFrame with errors for each model across folds and aggregated sMAPE/MASE.
    """
    n = len(series)
    # determine last training end index for which we can test horizon h
    if n - min_train - h < 0:
        raise ValueError("Not enough observations to perform rolling CV with the requested min_train and h.")
    # folds: train_end indices (inclusive) from min_train-1 to n-h-1
    folds = list(range(min_train, n - h + 1))  # fold uses training upto index fold-1? We'll use slice [0:fold]
    results = []
    for fold_end in tqdm(folds, desc="CV folds"):
        train = series.iloc[:fold_end].copy()
        test = series.iloc[fold_end:fold_end + h].copy()
        # compute forecasts from each model
        preds = {}
        # 1) seasonal naive
        preds['seasonal_naive'] = seasonal_naive_forecast(train, h=h, seasonal_periods=SEASONAL_PERIODS)
        # 2) sma4
        preds['sma4'] = sma_forecast(train, h=h, window=4)
        # 3) ETS
        preds['ets'] = ets_forecast(train, h=h, seasonal_periods=SEASONAL_PERIODS)
        # 4) SARIMA grid search
        sarima_fc, sarima_model, sarima_order, sarima_failures  = sarima_grid_search_forecast(train, h=h, seasonal_periods=SEASONAL_PERIODS,
                                                                            p_values=SARIMA_P_VALUES,
                                                                            d_values=SARIMA_D_VALUES,
                                                                            q_values=SARIMA_Q_VALUES,
                                                                            P_values=SARIMA_P_SEASONAL,
                                                                            D_values=SARIMA_D_SEASONAL,
                                                                            Q_values=SARIMA_Q_SEASONAL)
        preds['sarima_grid'] = sarima_fc
        # 5) STL + ARIMA
        stl_fc, stl_model, stl_order = stl_deseasonalize_arima_forecast(train, h=h, seasonal_periods=SEASONAL_PERIODS)
        preds['stl_arima'] = stl_fc

        # Evaluate errors
        for mname, pf in preds.items():
            pf = np.asarray(pf, dtype=float).flatten()
            true = test.values.astype(float).flatten()

            # compute sMAPE and MASE using train for scaling
            try:
                score_smape = smape(true, pf)
            except Exception:
                score_smape = np.nan
            try:
                score_mase = mase(train.values.astype(float), true, pf)
            except Exception:
                score_mase = np.nan
            results.append({
                'fold_end_index': fold_end,
                'fold_train_end_ts': train.index[-1],
                'fold_test_start_ts': test.index[0],
                'model': mname,
                'smape': score_smape,
                'mase': score_mase
            })
    results_df = pd.DataFrame(results)
    # aggregate
    agg = results_df.groupby('model').agg({'smape': 'mean', 'mase': 'mean'}).reset_index().sort_values('smape')
    return results_df, agg

# -------------------------
# Run cross-validation and compare models
# -------------------------
# set a reasonable minimum train size: at least two seasonal cycles (preferable) but with 22 obs we set to MIN_TRAIN_SPLITS
min_train = MIN_TRAIN_SPLITS
try:
    cv_details, cv_agg = rolling_origin_evaluation(series, h=FORECAST_HORIZON, min_train=min_train)
except Exception as e:
    # fallback to a minimal rolling scheme with smaller min_train if initial fails
    print("Rolling CV failed with min_train =", min_train, "— falling back to min_train = 6. Error:", e)
    min_train = 6
    cv_details, cv_agg = rolling_origin_evaluation(series, h=FORECAST_HORIZON, min_train=min_train)

print("\nCross-validated aggregate performance (lower is better):")
print(cv_agg)

# Save CV results
cv_agg.to_csv("model_comparison.csv", index=False)
cv_details.to_csv("model_cv_folds_detailed.csv", index=False)

# -------------------------
# Select best model (by CV smape then mase)
# -------------------------
# prefer lowest sMAPE; break ties by MASE
cv_agg_sorted = cv_agg.sort_values(['smape', 'mase']).reset_index(drop=True)
best_model_name = cv_agg_sorted.loc[0, 'model']
print(f"\nSelected best model by CV: {best_model_name}")

# -------------------------
# Fit best model on full sample and produce final forecast
# -------------------------
full_train = series.copy()
n_full = len(full_train)

final_forecast = None
final_model_obj = None
final_model_info = None
final_conf_int = None

if best_model_name == 'seasonal_naive':
    final_forecast = seasonal_naive_forecast(full_train, h=FORECAST_HORIZON, seasonal_periods=SEASONAL_PERIODS)
    final_model_info = "seasonal_naive(t-4)"
elif best_model_name == 'sma4':
    final_forecast = sma_forecast(full_train, h=FORECAST_HORIZON, window=4)
    final_model_info = "sma4_mean_last4"
elif best_model_name == 'ets':
    try:
        model = ExponentialSmoothing(full_train, trend='add', seasonal='add',
                                     seasonal_periods=SEASONAL_PERIODS, initialization_method="estimated")
        fit = model.fit(optimized=True)
        fc = fit.forecast(FORECAST_HORIZON)
        final_forecast = np.asarray(fc)
        final_model_obj = fit
        final_model_info = "ETS (add,add)"
        # ExponentialSmoothing in statsmodels does not provide conf_int easily; leave None
    except Exception as ex:
        print("ETS fit failed on full sample; falling back to SMA4. Error:", ex)
        final_forecast = sma_forecast(full_train, h=FORECAST_HORIZON, window=4)
        final_model_info = "SMA4 (fallback)"
elif best_model_name == 'sarima_grid':
    fc, res_model, order, _ = sarima_grid_search_forecast(full_train, h=FORECAST_HORIZON,
                                                       seasonal_periods=SEASONAL_PERIODS,
                                                       p_values=SARIMA_P_VALUES,
                                                       d_values=SARIMA_D_VALUES,
                                                       q_values=SARIMA_Q_VALUES,
                                                       P_values=SARIMA_P_SEASONAL,
                                                       D_values=SARIMA_D_SEASONAL,
                                                       Q_values=SARIMA_Q_SEASONAL)
    final_forecast = np.asarray(fc)
    final_model_obj = res_model
    final_model_info = f"SARIMA {order}"
    # try to get conf_int if possible
    if res_model is not None:
        try:
            pred_obj = res_model.get_forecast(steps=FORECAST_HORIZON)
            conf_df = pred_obj.conf_int(alpha=0.05)
            final_conf_int = conf_df.values.tolist()[0]
        except Exception:
            final_conf_int = None
elif best_model_name == 'stl_arima':
    fc, fitted_model, fitted_order = stl_deseasonalize_arima_forecast(full_train, h=FORECAST_HORIZON,
                                                                      seasonal_periods=SEASONAL_PERIODS)
    final_forecast = np.asarray(fc)
    final_model_obj = fitted_model
    final_model_info = f"STL_deseasonalize + ARIMA {fitted_order}"

# Build forecast timestamp index: forecast for the next FORECAST_HORIZON quarters after last observation
last_period = df_obs.index[-1].to_period('Q')
forecast_ts = [(last_period + i).to_timestamp() for i in range(1, FORECAST_HORIZON + 1)]
forecast_index = pd.Index(forecast_ts)

# Ensure final_forecast is array-like with correct length
final_forecast_array = np.asarray(final_forecast).flatten()
if len(final_forecast_array) != FORECAST_HORIZON:
    # If mismatch, repeat to match horizon
    final_forecast_array = np.repeat(final_forecast_array[0] if len(final_forecast_array) > 0 else np.nan, FORECAST_HORIZON)

forecast_df = pd.DataFrame({
    'forecast_ts': forecast_index,
    'model': best_model_name,
    'point_forecast': final_forecast_array
})
# attach confidence bounds if available
if final_conf_int is not None:
    forecast_df['lower_95'] = final_conf_int[0]
    forecast_df['upper_95'] = final_conf_int[1]
else:
    forecast_df['lower_95'] = np.nan
    forecast_df['upper_95'] = np.nan

forecast_df.to_csv("forecasts_full_fit.csv", index=False)

# -------------------------
# Output summary diagnostics (also saved to file)
# -------------------------
diag_lines = []
diag_lines.append(f"Forecast pipeline diagnostics - {datetime.utcnow().isoformat()} UTC")
diag_lines.append(f"Data path: {DATA_PATH}")
diag_lines.append(f"Series start: {series.index[0].date()} | end: {series.index[-1].date()} | observations: {len(series)}")
diag_lines.append(f"Seasonal periods: {SEASONAL_PERIODS}")
diag_lines.append(f"Cross-validated model ranking (by mean sMAPE):")
diag_lines.append(cv_agg_sorted.to_string(index=False))
diag_lines.append("")
diag_lines.append(f"Selected model: {best_model_name} ({final_model_info})")
diag_lines.append(f"Forecast horizon (steps): {FORECAST_HORIZON}")
diag_lines.append(f"Forecast timestamp(s): {[ts.date() for ts in forecast_index]}")
diag_lines.append(f"Point forecast(s): {final_forecast.tolist()}")
if final_conf_int is not None:
    diag_lines.append(f"95% conf interval for forecast: {final_conf_int}")
diag_text = "\n".join(diag_lines)

print("\n" + diag_text + "\n")

with open("model_diagnostics.txt", "w", encoding="utf-8") as fh:
    fh.write(diag_text)

# Also print the CSV path locations
print("Saved outputs:")
print("- model_comparison.csv (CV aggregated metrics)")
print("- model_cv_folds_detailed.csv (CV fold-level metrics)")
print("- forecasts_full_fit.csv (final forecast(s))")
print("- model_diagnostics.txt (detailed diagnostics)")

# End of script
