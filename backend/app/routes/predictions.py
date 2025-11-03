"""
Proqnozlaşdırma və Gələcək Təxminləri Endpoint-ləri
Predictions and Forecasting Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
import math

from app.utils.data_loader import data_loader

router = APIRouter()

def clean_value(val):
    """Clean value for JSON serialization"""
    if pd.isna(val) or (isinstance(val, (int, float)) and math.isinf(val)):
        return 0.0
    if isinstance(val, (np.integer, np.floating)):
        return float(val)
    if isinstance(val, np.bool_):
        return bool(val)
    return val

# Model paths
# Use environment variable to determine path or auto-detect
import os
if os.getenv('ENVIRONMENT') == 'production':
    # Docker: /app/app/routes/predictions.py -> /app/notebooks/predictions/models
    MODELS_DIR = Path(__file__).parent.parent.parent / "notebooks" / "predictions" / "models"
else:
    # Local: backend/app/routes/predictions.py -> notebooks/predictions/models
    MODELS_DIR = Path(__file__).parent.parent.parent.parent / "notebooks" / "predictions" / "models"


@router.get("/simple-forecast", response_model=Dict[str, Any])
async def get_simple_forecast(
    periods: int = Query(default=4, ge=1, le=12, description="Proqnoz dövrləri (1-12 rüb)")
):
    """
    🔮 Sadə Proqnoz

    Moving Average və Exponential Smoothing əsasında sadə proqnoz

    Parameters:
    - periods: Gələcək neçə rüb üçün proqnoz (1-12 arası)
    """
    df = data_loader.df

    # Filter out rows with empty/NaN target values
    df_valid = df[df['Nağd_pul_kredit_satışı'].notna()].copy()
    y = df_valid['Nağd_pul_kredit_satışı'].values

    # Son dəyərlər (from last valid row)
    last_period = df_valid['Rüblər'].iloc[-1]
    last_year = df_valid['Year'].iloc[-1]
    last_quarter = df_valid['Quarter'].iloc[-1]
    last_value = y[-1]

    # 1. Moving Average (son 4 rüb)
    ma_4 = np.mean(y[-4:])

    # 2. Weighted Moving Average (son 4 rüb, çəkilər: 0.4, 0.3, 0.2, 0.1)
    weights = np.array([0.1, 0.2, 0.3, 0.4])
    wma_4 = np.sum(y[-4:] * weights)

    # 3. Exponential Smoothing (alpha=0.3)
    alpha = 0.3
    ema = y[0]
    for val in y[1:]:
        ema = alpha * val + (1 - alpha) * ema

    # 4. Trend-based forecast (son 8 rüb üzrə xətti trend)
    recent_periods = np.arange(len(y[-8:]))
    recent_values = y[-8:]
    trend_coef = np.polyfit(recent_periods, recent_values, 1)
    trend_slope = trend_coef[0]
    trend_intercept = trend_coef[1]

    # Proqnozlar
    forecasts = []
    for i in range(1, periods + 1):
        # Dövrü hesabla
        quarter = ((last_quarter + i - 1) % 4) + 1
        year = last_year + (last_quarter + i - 1) // 4
        period_name = f"{year}-Q{quarter}"

        # Müxtəlif metodlarla proqnozlar
        ma_forecast = ma_4
        wma_forecast = wma_4
        ema_forecast = ema
        trend_forecast = trend_slope * (len(y) + i - 1) + trend_intercept

        # Kombinə olunmuş proqnoz (bütün metodların ortalaması)
        combined_forecast = np.mean([ma_forecast, wma_forecast, ema_forecast, trend_forecast])

        # Confidence interval (sadə yanaşma - son dəyərlərin standart sapması)
        std = np.std(y[-8:])
        lower_bound = combined_forecast - 1.96 * std  # 95% CI
        upper_bound = combined_forecast + 1.96 * std

        forecasts.append({
            "dövr": period_name,
            "il": int(year),
            "rüb": int(quarter),
            "kombinə_proqnoz": round(clean_value(combined_forecast), 2),
            "aşağı_sərhəd_95": round(clean_value(lower_bound), 2),
            "yuxarı_sərhəd_95": round(clean_value(upper_bound), 2),
            "metodlar": {
                "moving_average": round(clean_value(ma_forecast), 2),
                "weighted_ma": round(clean_value(wma_forecast), 2),
                "exponential_smoothing": round(clean_value(ema_forecast), 2),
                "trend_based": round(clean_value(trend_forecast), 2)
            }
        })

    # Metodların izahı
    method_explanations = {
        "moving_average": {
            "ad": "Hərəkətli Ortalama (Moving Average)",
            "təsvir": "Son 4 rübün sadə ortalaması",
            "üstünlük": "Sadə və anlaşılan",
            "çatışmazlıq": "Trend və mövsümiliyi nəzərə almır",
            "uyğunluq": "Sabit məlumatlar üçün"
        },
        "weighted_ma": {
            "ad": "Çəkili Hərəkətli Ortalama (Weighted MA)",
            "təsvir": "Yaxın dövrlərin çəkisi daha çoxdur (40%, 30%, 20%, 10%)",
            "üstünlük": "Son dəyişikliklərə daha həssas",
            "çatışmazlıq": "Çəkilərin seçimi subyektivdir",
            "uyğunluq": "Trendli məlumatlar üçün"
        },
        "exponential_smoothing": {
            "ad": "Eksponensial Hamarlaşdırma",
            "təsvir": "Bütün keçmiş dəyərlər nəzərə alınır, lakin yaxın dövrlərin təsiri daha güclüdür (α=0.3)",
            "üstünlük": "Bütün tarixi nəzərə alır",
            "çatışmazlıq": "Alpha parametrinin seçimi mühümdür",
            "uyğunluq": "Uzun tarixli məlumatlar üçün"
        },
        "trend_based": {
            "ad": "Trend Əsaslı Proqnoz",
            "təsvir": "Son 8 rübün xətti trendi əsasında",
            "üstünlük": "Trend davam edərsə dəqiqdir",
            "çatışmazlıq": "Qırılma nöqtələrini tutmur",
            "uyğunluq": "Güclü trend olan məlumatlar üçün"
        }
    }

    # Proqnoz keyfiyyəti
    actual_vs_pred = []
    for i in range(4, len(y)):
        actual = y[i]
        pred_ma = np.mean(y[i-4:i])
        actual_vs_pred.append({
            "faktiki": clean_value(actual),
            "proqnoz": clean_value(pred_ma),
            "xəta": clean_value(abs(actual - pred_ma)),
            "xəta_faizi": clean_value(abs(actual - pred_ma) / actual * 100 if actual != 0 else 0)
        })

    avg_error = clean_value(np.mean([x["xəta"] for x in actual_vs_pred]))
    avg_error_pct = clean_value(np.mean([x["xəta_faizi"] for x in actual_vs_pred]))

    return {
        "proqnoz_nədir": {
            "təsvir": "Proqnozlaşdırma - keçmiş məlumatlar əsasında gələcək dəyərləri təxmin etmə prosesidir.",
            "niyə_vacibdir": [
                "Gələcək planlaşdırma və büdcə tərtibatı üçün",
                "Resursların səmərəli bölüşdürülməsi üçün",
                "Risklərin əvvəlcədən müəyyən edilməsi üçün",
                "İş strategiyalarının hazırlanması üçün"
            ],
            "nə_zaman_istifadə": "Zaman seriyası məlumatlarında gələcək dəyərləri təxmin etmək istədikdə"
        },
        "cari_vəziyyət": {
            "son_dövr": last_period,
            "son_dəyər": round(clean_value(last_value), 2),
            "son_4_rüb_ortalama": round(clean_value(ma_4), 2),
            "dəyişiklik": round(clean_value(last_value - ma_4), 2),
            "dəyişiklik_faizi": round(clean_value((last_value - ma_4) / ma_4 * 100 if ma_4 != 0 else 0), 2)
        },
        "proqnozlar": forecasts,
        "metodlar": method_explanations,
        "dəqiqlik_təhlili": {
            "ortalama_xəta": round(avg_error, 2),
            "ortalama_xəta_faizi": round(avg_error_pct, 2),
            "test_edilmiş_proqnozlar": len(actual_vs_pred),
            "qeyd": "Bu dəqiqlik göstəriciləri keçmiş məlumatlar üzrə Moving Average metodunun performansını əks etdirir"
        },
        "praktik_təfsir": {
            "əsas_nəticə": f"Növbəti rüb üçün gözlənilən dəyər {round(forecasts[0]['kombinə_proqnoz'], 2):,.0f} manat civarında olacaq",
            "etibarlılıq_aralığı": f"95% ehtimalla {round(forecasts[0]['aşağı_sərhəd_95'], 2):,.0f} - {round(forecasts[0]['yuxarı_sərhəd_95'], 2):,.0f} manat arasında",
            "tövsiyə": "Kombinə proqnoz daha etibarlıdır, çünki müxtəlif metodların güclü tərəflərini birləşdirir"
        }
    }


@router.get("/seasonal-forecast", response_model=Dict[str, Any])
async def get_seasonal_forecast(
    periods: int = Query(default=4, ge=1, le=8, description="Proqnoz dövrləri")
):
    """
    📅 Mövsümi Proqnoz

    Mövsümiliyi nəzərə alan proqnoz modeli
    Rüblər arası fərqləri və təkrar edilən nümunələri tutur
    """
    df = data_loader.df
    y = df['Nağd_pul_kredit_satışı'].values
    quarters = df['Quarter'].values

    last_period = df['Rüblər'].iloc[-1]
    last_year = df['Year'].iloc[-1]
    last_quarter = df['Quarter'].iloc[-1]

    # Hər rüb üçün ortalama
    seasonal_avg = {}
    for q in [1, 2, 3, 4]:
        q_values = y[quarters == q]
        seasonal_avg[q] = np.mean(q_values)

    # Ümumi ortalama
    overall_avg = np.mean(y)

    # Seasonal indices (mövsümilik indeksləri)
    seasonal_indices = {}
    for q in [1, 2, 3, 4]:
        seasonal_indices[q] = seasonal_avg[q] / overall_avg

    # Trend (son 12 rüb)
    recent_y = y[-12:] if len(y) >= 12 else y
    recent_x = np.arange(len(recent_y))
    trend_coef = np.polyfit(recent_x, recent_y, 1)
    trend_slope = trend_coef[0]
    trend_intercept = trend_coef[1]

    # Proqnozlar
    forecasts = []
    for i in range(1, periods + 1):
        quarter = ((last_quarter + i - 1) % 4) + 1
        year = last_year + (last_quarter + i - 1) // 4
        period_name = f"{year}-Q{quarter}"

        # Trend dəyəri
        trend_value = trend_slope * (len(y) + i - 1) + trend_intercept

        # Mövsümilik tətbiq et
        seasonal_forecast = trend_value * seasonal_indices[quarter]

        # Confidence interval
        # Hər rübün keçmiş dəyərlərinin variasiyası
        q_historical = y[quarters == quarter]
        q_std = np.std(q_historical)

        lower_bound = seasonal_forecast - 1.96 * q_std
        upper_bound = seasonal_forecast + 1.96 * q_std

        forecasts.append({
            "dövr": period_name,
            "il": int(year),
            "rüb": int(quarter),
            "proqnoz": round(seasonal_forecast, 2),
            "aşağı_sərhəd_95": round(lower_bound, 2),
            "yuxarı_sərhəd_95": round(upper_bound, 2),
            "komponenlər": {
                "trend_komponenti": round(trend_value, 2),
                "mövsümi_indeks": round(seasonal_indices[quarter], 4),
                "mövsümi_təsir": round((seasonal_indices[quarter] - 1) * 100, 2)
            }
        })

    # Mövsümilik təhlili
    seasonal_analysis = {}
    for q in [1, 2, 3, 4]:
        q_values = y[quarters == q]
        seasonal_analysis[f"Q{q}"] = {
            "ortalama": round(seasonal_avg[q], 2),
            "indeks": round(seasonal_indices[q], 4),
            "ümumi_ortalamadan_fərq": round((seasonal_indices[q] - 1) * 100, 2),
            "izah": "Ümumi ortalamadan yüksək" if seasonal_indices[q] > 1 else "Ümumi ortalamadan aşağı",
            "keçmiş_dəyərlər_sayı": len(q_values),
            "standart_sapma": round(np.std(q_values), 2)
        }

    return {
        "mövsümi_proqnoz_nədir": {
            "təsvir": "Mövsümi proqnozlaşdırma - il içində təkrar edilən nümunələri (rüblər arası fərqləri) nəzərə alan proqnoz metodudur.",
            "komponentlər": [
                "Trend: Ümumi artım və ya azalma istiqaməti",
                "Mövsümililik: Rüblər arası təkrar edilən fərqlər",
                "Təsadüfi: İzah edilməyən variasiya"
            ],
            "üstünlük": "Kredit satışı kimi mövsümi xarakterli məlumatlar üçün daha dəqiqdir",
            "nə_zaman_istifadə": "Məlumatlar aydın mövsümi nümunə göstərdikdə"
        },
        "mövsümilik_təhlili": seasonal_analysis,
        "trend_məlumatı": {
            "istiqamət": "Artım" if trend_slope > 0 else "Azalma",
            "rüb_başına_dəyişmə": round(trend_slope, 2),
            "il_başına_dəyişmə": round(trend_slope * 4, 2),
            "trend_gücü": "Güclü" if abs(trend_slope) > 1000 else "Orta" if abs(trend_slope) > 500 else "Zəif"
        },
        "proqnozlar": forecasts,
        "praktik_təfsir": {
            "ən_güclü_rüb": f"Q{max(seasonal_indices, key=seasonal_indices.get)}",
            "ən_zəif_rüb": f"Q{min(seasonal_indices, key=seasonal_indices.get)}",
            "mövsümi_fərq": round((max(seasonal_indices.values()) - min(seasonal_indices.values())) * 100, 2),
            "tövsiyə": "Mövsümi nümunələr ardıcıl olaraq, planlaşdırmada hər rübün xüsusiyyətlərini nəzərə alın"
        }
    }


@router.get("/confidence-levels", response_model=Dict[str, Any])
async def get_confidence_levels():
    """
    🎯 Etibar Səviyyələri və Proqnoz Dəqiqliyi

    Proqnozların nə qədər etibarlı olduğunu anlamaq üçün müxtəlif göstəricilər
    """
    df = data_loader.df
    y = df['Nağd_pul_kredit_satışı'].values

    # Son 4 rübə əsaslanan sadə proqnoz keyfiyyəti
    errors = []
    for i in range(8, len(y)):  # Son 14 proqnoz (22-8=14)
        actual = y[i]
        predicted = np.mean(y[i-4:i])
        error = actual - predicted
        abs_error = abs(error)
        pct_error = abs_error / actual * 100 if actual != 0 else 0

        errors.append({
            "xəta": error,
            "mütləq_xəta": abs_error,
            "faiz_xəta": pct_error
        })

    # Metrics
    mae = np.mean([e["mütləq_xəta"] for e in errors])
    rmse = np.sqrt(np.mean([e["xəta"]**2 for e in errors]))
    mape = np.mean([e["faiz_xəta"] for e in errors])

    # Forecast accuracy classification
    if mape < 10:
        accuracy_class = "Çox Yüksək"
        description = "Proqnozlar çox etibarlıdır"
    elif mape < 20:
        accuracy_class = "Yüksək"
        description = "Proqnozlar yaxşı dəqiqliyə malikdir"
    elif mape < 30:
        accuracy_class = "Orta"
        description = "Proqnozlar qəbul edilə bilər, lakin ehtiyatla yanaşın"
    else:
        accuracy_class = "Aşağı"
        description = "Proqnozlar az etibarlıdır, əlavə təkmilləşdirmə lazımdır"

    # Confidence intervals
    std_error = np.std([e["xəta"] for e in errors])

    confidence_intervals = {
        "68%": {
            "aralıq": f"±{round(std_error, 2):,.0f} manat",
            "izah": "Proqnozların təxminən 68%-i bu aralıqda olacaq (1 standart sapma)"
        },
        "95%": {
            "aralıq": f"±{round(1.96 * std_error, 2):,.0f} manat",
            "izah": "Proqnozların təxminən 95%-i bu aralıqda olacaq (1.96 standart sapma)"
        },
        "99%": {
            "aralıq": f"±{round(2.58 * std_error, 2):,.0f} manat",
            "izah": "Proqnozların təxminən 99%-i bu aralıqda olacaq (2.58 standart sapma)"
        }
    }

    return {
        "etibar_səviyyələri_nədir": {
            "təsvir": "Etibar səviyyəsi proqnozun nə qədər etibarlı olduğunu göstərir. 95% etibar səviyyəsi o deməkdir ki, 100 proqnozdan 95-i bu aralıqda olacaq.",
            "praktik_istifadə": [
                "Risk idarəetməsi üçün: Ən pis və ən yaxşı ssenariləri müəyyən edin",
                "Planlaşdırma üçün: Ehtiyat fondları və resursları hesablayın",
                "Qərar qəbul etmə üçün: Proqnozun etibarlılığını qiymətləndirin"
            ],
            "seçim": "95% etibar səviyyəsi ən çox istifadə olunur (elmi standart)"
        },
        "dəqiqlik_göstəriciləri": {
            "MAE": {
                "dəyər": round(mae, 2),
                "ad": "Mean Absolute Error (Ortalama Mütləq Xəta)",
                "izah": "Ortalama olaraq proqnozlar faktiki dəyərdən bu qədər fərqlənir",
                "vahid": "manat"
            },
            "RMSE": {
                "dəyər": round(rmse, 2),
                "ad": "Root Mean Squared Error (Kök Ortalama Kvadrat Xəta)",
                "izah": "Böyük xətaları daha çox cəzalandıran ölçü. MAE-dən böyükdürsə, bəzi proqnozlar çox səhvdir",
                "vahid": "manat"
            },
            "MAPE": {
                "dəyər": round(mape, 2),
                "ad": "Mean Absolute Percentage Error (Ortalama Mütləq Faiz Xəta)",
                "izah": "Xətanın faktiki dəyərə nisbətən faizi. Müxtəlif miqyaslı məlumatları müqayisə etmək üçün",
                "vahid": "%"
            }
        },
        "proqnoz_keyfiyyəti": {
            "sinif": accuracy_class,
            "təsvir": description,
            "əsaslandırma": f"MAPE = {round(mape, 2)}% ({accuracy_class} dəqiqlik)",
            "standart": {
                "Çox Yüksək": "MAPE < 10%",
                "Yüksək": "10% ≤ MAPE < 20%",
                "Orta": "20% ≤ MAPE < 30%",
                "Aşağı": "MAPE ≥ 30%"
            }
        },
        "etibar_aralıqları": confidence_intervals,
        "test_edilən_proqnozlar": {
            "sayı": len(errors),
            "ortalama_xəta": round(np.mean([e["xəta"] for e in errors]), 2),
            "pozitiv_xətalar": len([e for e in errors if e["xəta"] > 0]),
            "neqativ_xətalar": len([e for e in errors if e["xəta"] < 0]),
            "izah": "Pozitiv xəta: proqnoz faktikidən kiçikdir. Neqativ xəta: proqnoz faktikidən böyükdür"
        },
        "praktik_tövsiyə": {
            "planlaşdırma_üçün": f"Növbəti rüb üçün proqnozu ±{round(1.96 * std_error, 2):,.0f} manat etibar aralığı ilə istifadə edin",
            "risk_idarəetməsi": f"Ən pis ssenari üçün proqnozdan {round(1.96 * std_error, 2):,.0f} manat aşağı dəyər nəzərə alın",
            "təkmilləşdirmə": "Əgər MAPE > 20% isə, əlavə dəyişənlər əlavə edin və ya daha mürəkkəb model istifadə edin"
        }
    }


@router.get("/advanced-models-info", response_model=Dict[str, Any])
async def get_advanced_models_info():
    """
    🤖 Advanced ML Models Information

    Returns information about all trained advanced models
    """
    try:
        model_info_path = MODELS_DIR / "model_info.json"

        if not model_info_path.exists():
            return {
                "status": "not_trained",
                "message": "Advanced models have not been trained yet. Please run the training notebook first.",
                "notebook_path": "notebooks/predictions/advanced_forecasting_models.ipynb"
            }

        with open(model_info_path, 'r', encoding='utf-8') as f:
            model_info = json.load(f)

        return {
            "status": "ready",
            "models": model_info['models'],
            "best_model": model_info['best_model'],
            "training_date": model_info['training_date']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model info: {str(e)}")


@router.post("/advanced-forecast", response_model=Dict[str, Any])
async def get_advanced_forecast(
    model_name: str = Query(..., description="Model: random_forest, xgboost, arima, sarima, sarimax"),
    n_periods: int = Query(default=4, ge=1, le=8, description="Number of periods to forecast")
):
    """
    🚀 Advanced Model Forecasting

    Make predictions using trained ML/Time Series models
    """
    try:
        # Check if models exist
        if not MODELS_DIR.exists():
            raise HTTPException(
                status_code=404,
                detail="Models directory not found. Please train models first."
            )

        # Load model info
        model_info_path = MODELS_DIR / "model_info.json"
        if not model_info_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Models not trained yet. Please run the training notebook."
            )

        with open(model_info_path, 'r', encoding='utf-8') as f:
            model_info = json.load(f)

        # Find model details
        model_details = next((m for m in model_info['models'] if m['id'] == model_name), None)
        if not model_details:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model name: {model_name}. Available: random_forest, xgboost, arima, sarima, sarimax"
            )

        df = data_loader.df

        # Prepare forecast based on model type
        if model_name in ['random_forest', 'xgboost']:
            # Load ML model and scaler
            model_path = MODELS_DIR / f"{model_name}.pkl"
            scaler_path = MODELS_DIR / "scaler.pkl"

            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)

            # Load feature importance
            fi_prefix = "rf" if model_name == "random_forest" else "xgb"
            fi_path = MODELS_DIR / f"{fi_prefix}_feature_importance.csv"
            feature_importance = pd.read_csv(fi_path).head(10).to_dict('records')

            # Simple prediction (using last known lags)
            # This is simplified - in production you'd do recursive forecasting
            last_values = df['Nağd_pul_kredit_satışı'].iloc[-4:].values
            last_year = df['Year'].iloc[-1]
            last_quarter = df['Quarter'].iloc[-1]

            forecasts = []
            for i in range(1, n_periods + 1):
                q = ((last_quarter + i - 1) % 4) + 1
                y = last_year + (last_quarter + i - 1) // 4

                # Create feature vector (simplified)
                features = {
                    'Year': y,
                    'Quarter': q,
                    'Time_Index': len(df) + i - 1,
                    'Quarter_Sin': np.sin(2 * np.pi * q / 4),
                    'Quarter_Cos': np.cos(2 * np.pi * q / 4),
                    'Lag_1': last_values[-1],
                    'Lag_2': last_values[-2],
                    'Lag_3': last_values[-3],
                    'Lag_4': last_values[-4] if len(last_values) > 3 else last_values[0],
                    'Rolling_Mean_2': np.mean(last_values[-2:]),
                    'Rolling_Mean_3': np.mean(last_values[-3:]),
                    'Rolling_Mean_4': np.mean(last_values[-4:]),
                    'Rolling_Std_2': np.std(last_values[-2:]),
                    'Rolling_Std_3': np.std(last_values[-3:]),
                    'Rolling_Std_4': np.std(last_values[-4:]),
                    'Diff_1': 0,
                    'Diff_4': 0
                }

                X = pd.DataFrame([features])
                X_scaled = scaler.transform(X)
                pred = model.predict(X_scaled)[0]

                # Simple confidence interval
                std = np.std(last_values)

                forecasts.append({
                    "dövr": f"{y}-Q{q}",
                    "il": int(y),
                    "rüb": int(q),
                    "proqnoz": round(float(pred), 2),
                    "aşağı_sərhəd_95": round(float(pred - 1.96 * std), 2),
                    "yuxarı_sərhəd_95": round(float(pred + 1.96 * std), 2)
                })

            return {
                "model": model_details,
                "proqnozlar": forecasts,
                "feature_importance": feature_importance,
                "model_type": "Machine Learning"
            }

        elif model_name in ['arima', 'sarima', 'sarimax']:
            # Load time series model
            from statsmodels.tsa.statespace.sarimax import SARIMAXResults
            from statsmodels.tsa.arima.model import ARIMAResults

            model_path = MODELS_DIR / f"{model_name}.pkl"

            if model_name == 'arima':
                model = ARIMAResults.load(model_path)
            else:
                model = SARIMAXResults.load(model_path)

            # Make forecast
            last_year = df['Year'].iloc[-1]
            last_quarter = df['Quarter'].iloc[-1]

            if model_name == 'sarimax':
                # Need exogenous variables for SARIMAX
                exog_future = []
                for i in range(1, n_periods + 1):
                    q = ((last_quarter + i - 1) % 4) + 1
                    y = last_year + (last_quarter + i - 1) // 4
                    exog_future.append({'Year': y, 'Quarter': q})

                exog_df = pd.DataFrame(exog_future)
                forecast_result = model.forecast(steps=n_periods, exog=exog_df)
                # Get confidence intervals with exog
                forecast_obj = model.get_forecast(steps=n_periods, exog=exog_df)
                forecast_ci = forecast_obj.conf_int()
            else:
                forecast_result = model.forecast(steps=n_periods)
                # Get confidence intervals without exog
                forecast_ci = model.get_forecast(steps=n_periods).conf_int()

            last_year = df['Year'].iloc[-1]
            last_quarter = df['Quarter'].iloc[-1]

            forecasts = []
            for i in range(n_periods):
                q = ((last_quarter + i) % 4) + 1
                y = last_year + (last_quarter + i) // 4

                forecasts.append({
                    "dövr": f"{y}-Q{q}",
                    "il": int(y),
                    "rüb": int(q),
                    "proqnoz": round(float(forecast_result.iloc[i]), 2),
                    "aşağı_sərhəd_95": round(float(forecast_ci.iloc[i, 0]), 2),
                    "yuxarı_sərhəd_95": round(float(forecast_ci.iloc[i, 1]), 2)
                })

            return {
                "model": model_details,
                "proqnozlar": forecasts,
                "model_type": "Time Series"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")


@router.get("/model-comparison", response_model=Dict[str, Any])
async def get_model_comparison():
    """
    ⚖️ Model Müqayisəsi

    Müxtəlif proqnoz modellərinin performans müqayisəsi
    """
    df = data_loader.df
    y = df['Nağd_pul_kredit_satışı'].values
    quarters = df['Quarter'].values

    # Test set: son 4 rüb
    train_y = y[:-4]
    test_y = y[-4:]
    test_quarters = quarters[-4:]

    # Model 1: Naive (Son dəyər)
    naive_pred = np.repeat(train_y[-1], 4)
    naive_mae = np.mean(np.abs(test_y - naive_pred))

    # Model 2: Moving Average (4 period)
    ma_pred = np.repeat(np.mean(train_y[-4:]), 4)
    ma_mae = np.mean(np.abs(test_y - ma_pred))

    # Model 3: Seasonal Naive
    seasonal_naive_pred = []
    for q in test_quarters:
        historical_q = train_y[quarters[:-4] == q]
        if len(historical_q) > 0:
            seasonal_naive_pred.append(historical_q[-1])
        else:
            seasonal_naive_pred.append(train_y[-1])
    seasonal_naive_pred = np.array(seasonal_naive_pred)
    seasonal_naive_mae = np.mean(np.abs(test_y - seasonal_naive_pred))

    # Model 4: Seasonal Average
    seasonal_avg_pred = []
    for q in test_quarters:
        historical_q = train_y[quarters[:-4] == q]
        if len(historical_q) > 0:
            seasonal_avg_pred.append(np.mean(historical_q))
        else:
            seasonal_avg_pred.append(np.mean(train_y))
    seasonal_avg_pred = np.array(seasonal_avg_pred)
    seasonal_avg_mae = np.mean(np.abs(test_y - seasonal_avg_pred))

    # Model 5: Linear Trend
    x_train = np.arange(len(train_y))
    x_test = np.arange(len(train_y), len(train_y) + 4)
    trend_coef = np.polyfit(x_train, train_y, 1)
    trend_pred = trend_coef[0] * x_test + trend_coef[1]
    trend_mae = np.mean(np.abs(test_y - trend_pred))

    # Nəticələr
    models = {
        "Naive": {
            "ad": "Naive Forecast",
            "təsvir": "Son dəyər gələcək dəyər kimi qəbul edilir",
            "mae": round(naive_mae, 2),
            "rank": 0,
            "üstünlük": "Ən sadə, hesablaması asan",
            "çatışmazlıq": "Trend və mövsümilik nəzərə alınmır",
            "uyğun_olduğu_vəziyyət": "Çox sabit məlumatlar"
        },
        "Moving_Average": {
            "ad": "Moving Average (MA-4)",
            "təsvir": "Son 4 rübün ortalaması",
            "mae": round(ma_mae, 2),
            "rank": 0,
            "üstünlük": "Səs-küyü azaldır, sabitdir",
            "çatışmazlıq": "Trend və mövsümiliyə az həssas",
            "uyğun_olduğu_vəziyyət": "Səs-küylü lakin trendsiz məlumatlar"
        },
        "Seasonal_Naive": {
            "ad": "Seasonal Naive",
            "təsvir": "Hər rüb üçün keçmiş ilin eyni rübünün dəyəri",
            "mae": round(seasonal_naive_mae, 2),
            "rank": 0,
            "üstünlük": "Mövsümiliyi tutur",
            "çatışmazlıq": "Trend nəzərə alınmır",
            "uyğun_olduğu_vəziyyət": "Güclü mövsümilik, zəif trend"
        },
        "Seasonal_Average": {
            "ad": "Seasonal Average",
            "təsvir": "Hər rüb üçün keçmiş bütün eyni rüblərin ortalaması",
            "mae": round(seasonal_avg_mae, 2),
            "rank": 0,
            "üstünlük": "Mövsümiliyi tutur, daha sabitdir",
            "çatışmazlıq": "Trend və son dəyişikliklərə az həssas",
            "uyğun_olduğu_vəziyyət": "Güclü mövsümilik, zəif trend"
        },
        "Linear_Trend": {
            "ad": "Linear Trend",
            "təsvir": "Xətti trendin davamı",
            "mae": round(trend_mae, 2),
            "rank": 0,
            "üstünlük": "Trendi tutur",
            "çatışmazlıq": "Mövsümilik nəzərə alınmır",
            "uyğun_olduğu_vəziyyət": "Güclü xətti trend"
        }
    }

    # Ranking
    sorted_models = sorted(models.items(), key=lambda x: x[1]["mae"])
    for i, (name, _) in enumerate(sorted_models, 1):
        models[name]["rank"] = i

    best_model = sorted_models[0][0]

    return {
        "model_müqayisəsi_nədir": {
            "təsvir": "Model müqayisəsi müxtəlif proqnoz metodlarının keçmiş məlumatlar üzrə performansını ölçür və ən yaxşı metodu müəyyən edir.",
            "metrika": "MAE (Mean Absolute Error) - ortalama mütləq xəta. Kiçik MAE = Daha yaxşı model",
            "test_metodu": "Son 4 rüb test məlumatı kimi ayrıldı, qalan məlumatlarla model quruldu",
            "niyə_vacibdir": "Hər məlumat toplusu üçün ən uyğun metodu seçmək proqnoz dəqiqliyini artırır"
        },
        "modellər": models,
        "nəticə": {
            "ən_yaxşı_model": models[best_model]["ad"],
            "mae": models[best_model]["mae"],
            "izah": f"{models[best_model]['ad']} modeli ən kiçik xətaya malikdir və bu məlumat toplusu üçün ən uyğundur",
            "tövsiyə": models[best_model]["uyğun_olduğu_vəziyyət"]
        },
        "praktik_tövsiyə": {
            "birinci_seçim": models[best_model]["ad"],
            "ehtiyat_seçim": models[sorted_models[1][0]]["ad"],
            "kombinə_yanaşma": "Ən yaxşı 2-3 metodun ortalama proqnozunu istifadə edərək riski azaltmaq olar",
            "məsləhət": "Model performansını müntəzəm yoxlayın və yeni məlumatlar əlavə olunduqca yenidən qiymətləndirin"
        }
    }
