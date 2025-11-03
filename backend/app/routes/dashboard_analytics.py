"""
Dashboard Analytics Routes - For Next.js Analytics Dashboard
"""

from fastapi import APIRouter, HTTPException
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
                "gdp_growth": round(clean_value(row.get('GDP_artım_faizi', 0)), 2),
                "inflation": round(clean_value(row.get('İnflyasiya', 0)), 2),
                "unemployment": round(clean_value(row.get('İşsizlik_dərəcəsi', 0)), 2),
                "oil_price": round(clean_value(row.get('Neft_qiyməti', 0)), 2),
                "exchange_rate": round(clean_value(row.get('Məzənnə_USD_AZN', 0)), 4)
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
            result.append({
                "quarter": quarter,
                "loan_sales": round(clean_value(row['Nağd_pul_kredit_satışı']), 2),
                "npl_ratio": round(clean_value(row.get('NPL_əmsalı', 0)), 2),
                "roa": round(clean_value(row.get('ROA', 0)), 4),
                "customer_count": round(clean_value(row.get('Müştəri_sayı', 0)), 0),
                "deposits": round(clean_value(row.get('Əmanətlər', 0)), 2)
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
            result.append({
                "quarter": quarter,
                "loan_sales": round(clean_value(row['Nağd_pul_kredit_satışı']), 2),
                "gdp_growth": round(clean_value(row.get('GDP_artım_faizi', 0)), 2),
                "inflation": round(clean_value(row.get('İnflyasiya', 0)), 2),
                "npl_ratio": round(clean_value(row.get('NPL_əmsalı', 0)), 2),
                "roa": round(clean_value(row.get('ROA', 0)), 4),
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
