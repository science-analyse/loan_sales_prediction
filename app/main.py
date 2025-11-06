"""
Loan Sales Prediction - FastAPI Application
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
import json
import pickle
import pandas as pd
import numpy as np
from typing import List, Optional
import sys

# Add notebooks directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "notebooks"))

app = FastAPI(title="Loan Sales Prediction API", version="1.0.0")

# Setup templates and static files
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Update paths
MODELS_DIR = BASE_DIR / "notebooks" / "prediction" / "models"
DATA_DIR = BASE_DIR / "notebooks" / "data"

# Load model registry at startup
MODEL_REGISTRY = None


def load_registry():
    """Load model registry"""
    global MODEL_REGISTRY
    registry_path = MODELS_DIR / "model_registry.json"
    with open(registry_path, 'r', encoding='utf-8') as f:
        MODEL_REGISTRY = json.load(f)
    return MODEL_REGISTRY


# Pydantic models
class PredictionRequest(BaseModel):
    model: str
    year: int
    quarter: int


class ComparisonRequest(BaseModel):
    models: List[str]
    year: int
    quarter: int


# Load registry on startup
@app.on_event("startup")
async def startup_event():
    load_registry()
    print("✅ Model registry loaded")
    print(f"📊 Total models: {MODEL_REGISTRY['metadata']['total_models']}")


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/models")
async def get_models():
    """Get all available models organized by type"""

    # Organize models by category
    ml_models = []
    ts_models = []

    for name, info in MODEL_REGISTRY['ml_models'].items():
        ml_models.append({
            'name': name,
            'type': 'ml',
            'metrics': info['metrics']
        })

    for name, info in MODEL_REGISTRY['ts_models'].items():
        ts_models.append({
            'name': name,
            'type': 'timeseries',
            'metrics': info['metrics']
        })

    # Sort by test_r2
    ml_models.sort(key=lambda x: x['metrics'].get('test_r2', -999), reverse=True)
    ts_models.sort(key=lambda x: x['metrics'].get('test_r2', -999), reverse=True)

    # Categorize models
    recommended = []
    advanced_ml = []
    time_series = []
    experimental = []

    # Top 5 performers
    all_models = ml_models + ts_models
    all_models.sort(key=lambda x: x['metrics'].get('test_r2', -999), reverse=True)

    for model in all_models[:5]:
        if model['metrics'].get('test_r2', -999) > 0.3:
            recommended.append(model['name'])

    # Advanced ML (good performance)
    for model in ml_models:
        if model['metrics'].get('test_r2', -999) > 0.1 and model['name'] not in recommended:
            advanced_ml.append(model['name'])

    # Time series
    for model in ts_models:
        time_series.append(model['name'])

    # Experimental (poor performance)
    for model in ml_models:
        if model['metrics'].get('test_r2', -999) <= 0.0:
            experimental.append(model['name'])

    return JSONResponse({
        'categories': {
            'recommended': recommended,
            'advanced_ml': advanced_ml,
            'time_series': time_series,
            'experimental': experimental
        },
        'models': {
            'ml': ml_models,
            'ts': ts_models
        },
        'total': len(ml_models) + len(ts_models)
    })


@app.get("/api/model/{model_name}")
async def get_model_info(model_name: str):
    """Get detailed information about a specific model"""

    # Search in ML models
    if model_name in MODEL_REGISTRY['ml_models']:
        info = MODEL_REGISTRY['ml_models'][model_name]
        return JSONResponse({
            'name': model_name,
            'type': 'ml',
            'filename': info['filename'],
            'metrics': info['metrics']
        })

    # Search in TS models
    if model_name in MODEL_REGISTRY['ts_models']:
        info = MODEL_REGISTRY['ts_models'][model_name]
        return JSONResponse({
            'name': model_name,
            'type': 'timeseries',
            'filename': info['filename'],
            'metrics': info['metrics']
        })

    return JSONResponse({'error': 'Model not found'}, status_code=404)


def load_model(model_name: str):
    """Load a trained model"""
    # Get model info
    if model_name in MODEL_REGISTRY['ml_models']:
        info = MODEL_REGISTRY['ml_models'][model_name]
    elif model_name in MODEL_REGISTRY['ts_models']:
        info = MODEL_REGISTRY['ts_models'][model_name]
    else:
        raise ValueError(f"Model {model_name} not found")

    # Load model file
    model_path = MODELS_DIR / info['filename']
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    return model, info


def load_historical_data():
    """Load historical sales data"""
    df = pd.read_csv(DATA_DIR / 'ml_ready_data.csv')
    return df[['Year', 'Quarter', 'Nağd_pul_kredit_satışı']].dropna()


def get_historical_sales(year: int, quarter: int, years_back: int = 3):
    """Get historical sales for the same quarter from previous years"""
    df = load_historical_data()

    historical = []
    for i in range(1, years_back + 1):
        target_year = year - i
        row = df[(df['Year'] == target_year) & (df['Quarter'] == quarter)]
        if not row.empty:
            historical.append({
                'year': int(target_year),
                'quarter': int(quarter),
                'sales': float(row['Nağd_pul_kredit_satışı'].iloc[0]),
                'sales_formatted': f"{float(row['Nağd_pul_kredit_satışı'].iloc[0]):,.2f}"
            })

    return historical


def prepare_ml_features():
    """Load PCA features for ML model prediction"""
    df_pca = pd.read_csv(DATA_DIR / 'pca_features.csv')

    # Get the last known features as template
    features = df_pca[['PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6']].iloc[-1].values

    return features.reshape(1, -1)


def prepare_ts_forecast(model, steps: int = 1, model_name: str = ""):
    """Make time series forecast"""
    try:
        # SARIMAX models need exogenous variables (time trend)
        if 'SARIMAX' in model_name:
            # Load historical data to get the time index
            df = load_historical_data()
            last_index = len(df)
            # Create exogenous variable (time trend) for next step
            exog_future = np.arange(last_index, last_index + steps).reshape(-1, 1)
            forecast = model.forecast(steps=steps, exog=exog_future)
        else:
            forecast = model.forecast(steps=steps)

        if isinstance(forecast, (list, np.ndarray)):
            return float(forecast[-1])
        # Handle pandas Series
        if hasattr(forecast, 'iloc'):
            return float(forecast.iloc[0])
        return float(forecast)
    except Exception as e:
        # Some models may fail - return None to indicate failure
        print(f"⚠️  Forecast failed for {model_name}: {str(e)}")
        return None


def calculate_scenarios(base_prediction: float, model_info: dict):
    """Calculate optimistic and pessimistic scenarios based on model performance"""
    # Get metrics with safe defaults
    mape = model_info['metrics'].get('test_mape', 15.0)  # Default 15% uncertainty
    mae = model_info['metrics'].get('test_mae', 0)

    # Determine uncertainty range
    # If MAE is available and non-zero, use it; otherwise fall back to MAPE
    if mae > 0:
        # Use MAE-based approach (absolute error)
        # Optimistic: better performance (lower error) = higher value
        # Pessimistic: worse performance (higher error) = lower value
        optimistic = base_prediction + mae * 0.5  # 50% of MAE improvement
        pessimistic = base_prediction - mae * 0.5  # 50% of MAE decline
    else:
        # Use MAPE-based approach (percentage error)
        # More robust when MAE is missing or zero
        uncertainty_pct = mape / 100.0  # Convert to decimal
        optimistic = base_prediction * (1 + uncertainty_pct * 0.5)  # 50% of MAPE improvement
        pessimistic = base_prediction * (1 - uncertainty_pct * 0.5)  # 50% of MAPE decline

    # Ensure scenarios are different from base (minimum 1% variation)
    min_variation = abs(base_prediction) * 0.01  # 1% of base
    if abs(optimistic - base_prediction) < min_variation:
        optimistic = base_prediction + min_variation
    if abs(pessimistic - base_prediction) < min_variation:
        pessimistic = base_prediction - min_variation

    return {
        'optimistic': float(optimistic),
        'optimistic_formatted': f"{optimistic:,.2f}",
        'base': float(base_prediction),
        'base_formatted': f"{base_prediction:,.2f}",
        'pessimistic': float(pessimistic),
        'pessimistic_formatted': f"{pessimistic:,.2f}",
        'uncertainty_mape': float(mape),
        'uncertainty_mae': float(mae)
    }


@app.post("/api/predict")
async def predict(request: PredictionRequest):
    """Make prediction for given year, quarter, and model with historical context and scenarios"""

    try:
        # Load model
        model, info = load_model(request.model)

        # Make prediction based on model type
        if info['type'] == 'ml':
            # ML models use PCA features
            features = prepare_ml_features()
            prediction = float(model.predict(features)[0])

        elif info['type'] == 'timeseries':
            # Time series models forecast ahead
            # For simplicity, we'll forecast 1 step ahead
            prediction = prepare_ts_forecast(model, steps=1, model_name=request.model)

            if prediction is None:
                return JSONResponse({
                    'error': 'Time series prediction failed',
                    'note': 'This model may require exogenous variables'
                }, status_code=400)

        else:
            return JSONResponse({'error': 'Unknown model type'}, status_code=400)

        # Get historical data for context (same quarter, previous years)
        historical = get_historical_sales(request.year, request.quarter, years_back=5)

        # Calculate optimistic and pessimistic scenarios
        scenarios = calculate_scenarios(prediction, info)

        # Return result with extended information
        return JSONResponse({
            'success': True,
            'model': request.model,
            'year': request.year,
            'quarter': request.quarter,
            'prediction': prediction,
            'prediction_formatted': f"{prediction:,.2f}",
            'scenarios': scenarios,
            'historical': historical,
            'metrics': info['metrics'],
            'type': info['type']
        })

    except Exception as e:
        return JSONResponse({
            'error': str(e),
            'success': False
        }, status_code=500)


@app.post("/api/compare")
async def compare(request: ComparisonRequest):
    """Compare predictions from multiple models with scenarios"""

    results = []

    # Get historical data once (same for all models)
    historical = get_historical_sales(request.year, request.quarter, years_back=5)

    for model_name in request.models:
        try:
            # Load model
            model, info = load_model(model_name)

            # Make prediction
            if info['type'] == 'ml':
                features = prepare_ml_features()
                prediction = float(model.predict(features)[0])
            elif info['type'] == 'timeseries':
                prediction = prepare_ts_forecast(model, steps=1, model_name=model_name)
                if prediction is None:
                    prediction = 0.0
            else:
                continue

            # Calculate scenarios for this model
            scenarios = calculate_scenarios(prediction, info)

            results.append({
                'model': model_name,
                'prediction': prediction,
                'prediction_formatted': f"{prediction:,.2f}",
                'scenarios': scenarios,
                'metrics': info['metrics'],
                'type': info['type']
            })

        except Exception as e:
            results.append({
                'model': model_name,
                'error': str(e),
                'success': False
            })

    # Sort by R² score
    results.sort(key=lambda x: x.get('metrics', {}).get('test_r2', -999), reverse=True)

    return JSONResponse({
        'success': True,
        'year': request.year,
        'quarter': request.quarter,
        'results': results,
        'historical': historical,
        'count': len(results)
    })


@app.get("/api/stats")
async def get_statistics():
    """Get overall statistics"""

    # Calculate statistics from registry
    ml_count = len(MODEL_REGISTRY['ml_models'])
    ts_count = len(MODEL_REGISTRY['ts_models'])

    # Find best models
    all_models = []

    for name, info in MODEL_REGISTRY['ml_models'].items():
        all_models.append({
            'name': name,
            'type': 'ML',
            'r2': info['metrics'].get('test_r2', -999),
            'mape': info['metrics'].get('test_mape', 999)
        })

    for name, info in MODEL_REGISTRY['ts_models'].items():
        all_models.append({
            'name': name,
            'type': 'Time Series',
            'r2': info['metrics'].get('test_r2', -999),
            'mape': info['metrics'].get('test_mape', 999)
        })

    # Sort by R²
    all_models.sort(key=lambda x: x['r2'], reverse=True)

    best_overall = all_models[0] if all_models else None
    best_ml = next((m for m in all_models if m['type'] == 'ML'), None)
    best_ts = next((m for m in all_models if m['type'] == 'Time Series'), None)

    return JSONResponse({
        'total_models': ml_count + ts_count,
        'ml_models': ml_count,
        'ts_models': ts_count,
        'best_overall': best_overall,
        'best_ml': best_ml,
        'best_ts': best_ts
    })


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        'status': 'healthy',
        'models_loaded': MODEL_REGISTRY is not None,
        'total_models': MODEL_REGISTRY['metadata']['total_models'] if MODEL_REGISTRY else 0
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
