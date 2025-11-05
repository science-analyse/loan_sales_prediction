# 🏦 Loan Sales Prediction System

> **Advanced Machine Learning System for Quarterly Loan Sales Forecasting**
> Built with 18 trained models, PCA feature engineering, and executive-ready web interface

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Models](https://img.shields.io/badge/Models-18-success.svg)](#-models)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Models](#-models)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Tech Stack](#-tech-stack)

---

## 🎯 Overview

This system predicts **quarterly loan sales** (Nağd pul kredit satışı) using 28 economic indicators transformed into 6 principal components via PCA.

### Key Metrics

| Metric                   | Value                 |
| ------------------------ | --------------------- |
| **Total Models**   | 18 (13 ML + 5 TS)     |
| **Best R² Score** | 0.4274 (Holt-Winters) |
| **Best MAPE**      | 7.13% (Lasso α=1.0)  |
| **Features**       | 6 (PCA from 28)       |
| **Training Data**  | 2007-2024 (Quarterly) |

### What It Provides

✅ **18 Trained Models** (13 ML + 5 Time Series)
✅ **Real-time Predictions** via REST API
✅ **Historical Context** (5 years of data)
✅ **Scenario Analysis** (Optimistic/Base/Pessimistic)
✅ **Executive Dashboard** (Mobile-responsive UI)

---

## ✨ Features

### 🔮 Prediction Capabilities

- **Single Model Prediction** - Get forecast from any of 18 models
- **Multi-Model Comparison** - Compare up to 5 models simultaneously
- **Scenario Planning** - View optimistic/base/pessimistic forecasts
- **Historical Context** - See 5 years of historical data for same quarter

### 📊 Data & Models

- **PCA Feature Engineering** - 28 economic indicators → 6 components
- **Diverse Model Types** - Linear, Tree-based, Boosting, Time Series
- **Real Trained Models** - All models trained on actual data (2007-2024)
- **Production Ready** - Serialized with pickle for fast loading

### 🎨 User Interface

- **Executive Dashboard** - Premium gradient design
- **Mobile Responsive** - Works on phones, tablets, desktops
- **Real-time Updates** - AJAX-powered predictions
- **Model Selection** - Organized by performance tiers

---

## 📁 Project Structure

```
loan_sales_prediction/
│
├── app/                          # FastAPI Web Application
│   ├── main.py                   # API routes & business logic
│   ├── static/
│   │   ├── css/style.css         # Premium responsive styles
│   │   └── js/main.js            # Client-side logic
│   └── templates/index.html      # Main web interface
│
├── notebooks/
│   ├── data/                     # Processed datasets
│   │   ├── ml_ready_data.csv     # Historical sales data
│   │   └── pca_features.csv      # PCA-transformed features
│   │
│   └── prediction/
│       ├── models/               # 18 trained models
│       │   ├── ml_*.pkl          # 13 ML models
│       │   ├── ts_*.pkl          # 5 Time Series models
│       │   ├── scaler.pkl        # Feature scaler
│       │   └── model_registry.json
│       └── train_all_models.py   # Training script
│
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Multi-container setup
├── .dockerignore                 # Docker build exclusions
├── requirements.txt              # Python dependencies
├── render.yaml                   # Render.com deployment
├── start.py                      # Local development server
├── test_all_models.py            # Automated testing
└── README.md                     # This file
```

---

## 🤖 Models

### Machine Learning Models (13)

| Model                       | R² Score | MAPE   | Type     |
| --------------------------- | --------- | ------ | -------- |
| **Lasso (α=1.0)** ⭐ | 0.4016    | 7.13%  | Linear   |
| **Ridge (α=1.0)**    | 0.3734    | 7.58%  | Linear   |
| **Ridge (α=10.0)**   | 0.3667    | 7.88%  | Linear   |
| **ElasticNet**        | 0.3665    | 7.80%  | Linear   |
| **Gradient Boosting** | 0.3360    | 8.70%  | Boosting |
| **XGBoost**           | 0.1804    | 8.98%  | Boosting |
| **Random Forest**     | 0.0181    | 10.44% | Ensemble |
| **AdaBoost**          | 0.0040    | 10.14% | Boosting |
| Decision Tree               | -0.9686   | 14.59% | Tree     |
| K-Nearest Neighbors         | -0.8323   | 12.42% | Instance |
| CatBoost                    | -2.2682   | 18.08% | Boosting |
| LightGBM                    | -7.6327   | 29.94% | Boosting |
| Support Vector Regression   | -8.0665   | 30.81% | Kernel   |

### Time Series Models (5)

| Model                            | R² Score | MAPE   | Type           |
| -------------------------------- | --------- | ------ | -------------- |
| **Holt-Winters** ⭐        | 0.4274    | 7.85%  | Exp Smoothing  |
| **SARIMA(1,1,1)(1,1,1,4)** | 0.0950    | 10.36% | Seasonal ARIMA |
| ARIMA(2,1,2)                     | -0.1166   | 10.70% | ARIMA          |
| ARIMA(1,1,1)                     | -0.1580   | 11.18% | ARIMA          |
| SARIMAX(1,1,1)(1,1,1,4)          | N/A       | N/A    | SARIMAX        |

### Performance Tiers

**Top Performers (R² > 0.3):**
🥇 Holt-Winters (0.4274)
🥈 Lasso α=1.0 (0.4016)
🥉 Ridge α=1.0 (0.3734)

**Advanced (R² > 0.1):**
Ridge α=10.0, ElasticNet, Gradient Boosting, XGBoost

**Experimental (R² < 0):**
Decision Tree, KNN, CatBoost, LightGBM, SVR

---

## 🔧 Installation

### Prerequisites

- Python 3.11+
- Docker (optional)
- 8GB RAM minimum
- 2GB disk space

### Local Setup

```bash
# Clone repository
git clone https://github.com/Ismat-Samadov/loan_sales_prediction.git
cd loan_sales_prediction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python start.py
```

Visit: **http://localhost:8001**

### Docker Setup

```bash
# Build and run
docker build -t loan-sales-prediction .
docker run -p 8000:8000 loan-sales-prediction
```

Visit: **http://localhost:8000**

---

## 🎮 Usage

### Web Interface

1. **Select Model** - Choose from 18 trained models
2. **Select Period** - Pick year and quarter (Q1-Q4)
3. **Get Prediction** - Click "Predict" for single model
4. **Compare Models** - Click "Compare Models" for analysis

### Python API

```python
import requests

# Make prediction
response = requests.post(
    'http://localhost:8001/api/predict',
    json={
        'model': 'Ridge (α=1.0)',
        'year': 2025,
        'quarter': 1
    }
)

data = response.json()
print(f"Prediction: {data['prediction_formatted']}")
print(f"R² Score: {data['metrics']['test_r2']}")
```

### Command Line

```bash
# Health check
curl http://localhost:8001/api/health

# Get all models
curl http://localhost:8001/api/models

# Make prediction
curl -X POST http://localhost:8001/api/predict \
  -H "Content-Type: application/json" \
  -d '{"model":"Ridge (α=1.0)","year":2025,"quarter":1}'
```

---

## 📡 API Documentation

### Base URL

```
http://localhost:8001
```

### Endpoints

#### `GET /api/health`

Health check

**Response:**

```json
{
  "status": "healthy",
  "models_loaded": true,
  "total_models": 18
}
```

#### `GET /api/models`

Get all available models with performance metrics

#### `POST /api/predict`

Make prediction with single model

**Request:**

```json
{
  "model": "Ridge (α=1.0)",
  "year": 2025,
  "quarter": 1
}
```

**Response:**

```json
{
  "success": true,
  "prediction": 125707885.55,
  "prediction_formatted": "125,707,885.55",
  "scenarios": {
    "optimistic": 129695855.59,
    "base": 125707885.55,
    "pessimistic": 121719915.52
  },
  "historical": [...],
  "metrics": {
    "test_r2": 0.3734,
    "test_mape": 7.578
  }
}
```

#### `POST /api/compare`

Compare multiple models

**Request:**

```json
{
  "models": ["Ridge (α=1.0)", "Lasso (α=1.0)", "Holt-Winters"],
  "year": 2025,
  "quarter": 1
}
```

---

## 🚀 Deployment

### Render.com (Recommended)

See [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) for detailed instructions.

**Quick Steps:**

1. Push to GitHub
2. Create Web Service on Render
3. Settings:
   - Runtime: **Docker**
   - Dockerfile Path: `./Dockerfile`
   - Environment: `PORT=8000`
4. Deploy

**Build Time:** ~3-5 minutes

### Environment Variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `PORT` | 8000    | Server port |

---

## 💻 Tech Stack

### Backend

- **FastAPI 0.104** - Modern Python web framework
- **Uvicorn 0.24** - ASGI server
- **Pydantic** - Data validation

### Machine Learning

- **scikit-learn 1.3.2** - ML algorithms
- **statsmodels 0.14.0** - Time series
- **xgboost 2.0.3** - Gradient boosting
- **lightgbm 4.1.0** - Gradient boosting
- **catboost 1.2.2** - Gradient boosting

### Data Processing

- **pandas 2.1.4** - Data manipulation
- **numpy 1.26.4** - Numerical computing

### Frontend

- **Vanilla JavaScript** - No frameworks
- **CSS3** - Responsive design
- **Chart.js Ready** - For future visualizations

### DevOps

- **Docker** - Containerization
- **Python 3.11** - Runtime
- **Git/GitHub** - Version control

---

## 📊 Performance

### Model Metrics

- **Training Time**: ~5 minutes (all 18 models)
- **Best R² Score**: 0.4274 (Holt-Winters)
- **Best MAPE**: 7.13% (Lasso α=1.0)
- **Training Data**: 2007-2024 (68 quarters)

### API Performance

- **Cold Start**: ~2 seconds
- **Warm Prediction**: <100ms
- **Model Loading**: Cached after first load
- **Memory Usage**: ~500MB (all models loaded)

---

## 🧪 Testing

```bash
# Test all 18 models
python test_all_models.py

# Expected output:
# ✅ ML Models Passed: 13/13
# ✅ TS Models Passed: 5/5  
# ✅ Total Passed: 18/18
# 🎉 ALL 18 MODELS WORKING PERFECTLY!
```

---

## 📈 Data Sources

The model is trained on **28 economic indicators** (2007-2024):

- **Macroeconomic**: GDP, Government Revenue/Spending, Population Income
- **Trade**: Foreign Trade, Exports, Imports, Oil Price
- **Banking**: Interest Rate, Portfolio, NPLs, ROA, ROE
- **Engineered**: NPL%, Time Index, Quarterly Seasonality

**Target Variable**: Nağd pul kredit satışı (Cash Loan Sales)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

**⭐ Star this repo if you find it helpful!**

---

*Last Updated: November 5, 2024*
*Version: 1.0.0*
*Status: Production Ready* ✅
