"""
Dashboard Analytics Routes - For Next.js Analytics Dashboard
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import math

from app.utils.data_loader import data_loader

router = APIRouter()

def clean_value(val):
    """Clean value for JSON serialization"""
    if pd.isna(val) or math.isinf(val) if isinstance(val, (int, float)) else False:
        return 0.0
    return float(val) if isinstance(val, (np.integer, np.floating)) else val

@router.get("/overview")
async def get_overview():
    """Overview KPIs and trends"""
    try:
        df = data_loader.df
        target = 'Nağd_pul_kredit_satışı'

        # KPIs
        current_val = float(df[target].iloc[-1])
        prev_val = float(df[target].iloc[-2]) if len(df) > 1 else current_val
        change = ((current_val - prev_val) / prev_val * 100) if prev_val != 0 else 0

        kpis = [
            {
                "metric": "Loan Sales",
                "value": current_val,
                "change": round(change, 2),
                "trend": "up" if change > 0 else "down" if change < 0 else "neutral"
            },
            {
                "metric": "Average Sales",
                "value": round(float(df[target].mean()), 2),
                "change": round(((current_val - df[target].mean()) / df[target].mean() * 100), 2),
                "trend": "up" if current_val > df[target].mean() else "down"
            },
            {
                "metric": "Total Records",
                "value": len(df),
                "change": 0,
                "trend": "neutral"
            }
        ]

        # Trends - last 12 quarters
        trends = []
        for _, row in df.tail(12).iterrows():
            quarter = f"{int(row['Year'])}-Q{int(row['Quarter'])}"
            trends.append({
                "quarter": quarter,
                "value": clean_value(row[target]),
                "gdp": clean_value(row.get('GDP', 0)),
                "inflation": clean_value(row.get('İnflyasiya', 0))
            })

        return {"kpis": kpis, "trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/economic-indicators")
async def get_economic_indicators():
    """Economic indicators time series"""
    try:
        df = data_loader.df
        result = []
        for _, row in df.tail(16).iterrows():
            quarter = f"{int(row['Year'])}-Q{int(row['Quarter'])}"
            result.append({
                "quarter": quarter,
                "gdp_growth": round(clean_value(row.get('GDP', 0)), 2),
                "inflation": round(clean_value(row.get('Uçot_faiz_dərəcəsi', 0)), 2),
                "unemployment": round(clean_value(row.get('Müştəri_sayı', 0)) / 1000, 2),  # Customer count as proxy
                "oil_price": round(clean_value(row.get('Oil_Price', 0)), 2),
                "exchange_rate": round(clean_value(row.get('Məzənnə_USD_AZN', 1.7)), 4)
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/banking-metrics")
async def get_banking_metrics():
    """Banking metrics time series"""
    try:
        df = data_loader.df
        result = []
        for _, row in df.tail(16).iterrows():
            quarter = f"{int(row['Year'])}-Q{int(row['Quarter'])}"
            # Calculate NPL ratio if not present
            npl_ratio = 0
            if 'NPLs' in df.columns and 'Portfel' in df.columns:
                portfolio = clean_value(row.get('Portfel', 1))
                npls = clean_value(row.get('NPLs', 0))
                npl_ratio = (npls / portfolio * 100) if portfolio > 0 else 0

            result.append({
                "quarter": quarter,
                "loan_sales": round(clean_value(row.get('Nağd_pul_kredit_satışı', 0)), 2),
                "npl_ratio": round(npl_ratio, 2),
                "roa": round(clean_value(row.get('ROA', 0)) * 100, 4),  # Convert to percentage
                "customer_count": round(clean_value(row.get('Müştəri_sayı', 0)), 0),
                "deposits": round(clean_value(row.get('Əhalinin_banklardakı_əmanətləri', 0)), 2)
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quarterly")
async def get_quarterly_data():
    """Combined quarterly data for all metrics"""
    try:
        df = data_loader.df
        result = []
        for _, row in df.tail(20).iterrows():
            quarter = f"{int(row['Year'])}-Q{int(row['Quarter'])}"
            # Calculate NPL ratio
            npl_ratio = 0
            if 'NPLs' in df.columns and 'Portfel' in df.columns:
                portfolio = clean_value(row.get('Portfel', 1))
                npls = clean_value(row.get('NPLs', 0))
                npl_ratio = (npls / portfolio * 100) if portfolio > 0 else 0

            result.append({
                "quarter": quarter,
                "loan_sales": round(clean_value(row.get('Nağd_pul_kredit_satışı', 0)), 2),
                "gdp_growth": round(clean_value(row.get('GDP', 0)), 2),
                "inflation": round(clean_value(row.get('Uçot_faiz_dərəcəsi', 0)), 2),
                "npl_ratio": round(npl_ratio, 2),
                "roa": round(clean_value(row.get('ROA', 0)) * 100, 4),
                "customer_count": round(clean_value(row.get('Müştəri_sayı', 0)), 0)
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlations")
async def get_correlations():
    """Correlation matrix for key variables"""
    try:
        df = data_loader.df
        cols = ['Nağd_pul_kredit_satışı', 'GDP', 'İnflyasiya', 'İşsizlik_dərəcəsi',
                'Neft_qiyməti', 'NPL_əmsalı', 'ROA']

        # Filter existing columns
        available_cols = [c for c in cols if c in df.columns]
        corr_df = df[available_cols].corr()

        # Map to English names
        name_map = {
            'Nağd_pul_kredit_satışı': 'Loan Sales',
            'GDP': 'GDP',
            'İnflyasiya': 'Inflation',
            'İşsizlik_dərəcəsi': 'Unemployment',
            'Neft_qiyməti': 'Oil Price',
            'NPL_əmsalı': 'NPL Ratio',
            'ROA': 'ROA'
        }

        variables = [name_map.get(c, c) for c in available_cols]
        matrix = corr_df.values.tolist()

        return {"variables": variables, "matrix": matrix}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simple-forecast")
async def get_simple_forecast(periods: int = Query(default=4, ge=1, le=12)):
    """Simple forecast for Next.js dashboard"""
    try:
        df = data_loader.df

        # Filter out rows with empty target values
        df_valid = df[df['Nağd_pul_kredit_satışı'].notna()].copy()
        y = df_valid['Nağd_pul_kredit_satışı'].values

        # Get last valid values
        last_year = int(df_valid['Year'].iloc[-1])
        last_quarter = int(df_valid['Quarter'].iloc[-1])

        # Historical data (last 12 quarters)
        historical = []
        for _, row in df_valid.tail(12).iterrows():
            quarter = f"{int(row['Year'])}-Q{int(row['Quarter'])}"
            historical.append({
                "quarter": quarter,
                "actual": round(clean_value(row['Nağd_pul_kredit_satışı']), 2)
            })

        # Simple forecast logic
        ma_4 = np.mean(y[-4:])
        weights = np.array([0.1, 0.2, 0.3, 0.4])
        wma_4 = np.sum(y[-4:] * weights)

        # Exponential smoothing
        alpha = 0.3
        ema = y[0]
        for val in y[1:]:
            ema = alpha * val + (1 - alpha) * ema

        # Trend
        recent_periods = np.arange(len(y[-8:]))
        recent_values = y[-8:]
        trend_coef = np.polyfit(recent_periods, recent_values, 1)
        trend_slope = trend_coef[0]
        trend_intercept = trend_coef[1]

        # Generate forecasts
        forecast = []
        std = np.std(y[-8:])

        for i in range(1, periods + 1):
            quarter = ((last_quarter + i - 1) % 4) + 1
            year = last_year + (last_quarter + i - 1) // 4
            period_name = f"{year}-Q{quarter}"

            # Methods
            ma_forecast = ma_4
            wma_forecast = wma_4
            ema_forecast = ema
            trend_forecast = trend_slope * (len(y) + i - 1) + trend_intercept

            # Combined
            combined = np.mean([ma_forecast, wma_forecast, ema_forecast, trend_forecast])
            lower = combined - 1.96 * std
            upper = combined + 1.96 * std

            forecast.append({
                "quarter": period_name,
                "predicted": round(clean_value(combined), 2),
                "lower_bound": round(clean_value(lower), 2),
                "upper_bound": round(clean_value(upper), 2)
            })

        return {
            "historical": historical,
            "forecast": forecast
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
