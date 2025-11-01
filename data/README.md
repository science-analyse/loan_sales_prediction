# ML-Ready Dataset Documentation

## 📁 Files in this Directory

### 1. **raw_data.xlsx** (16 KB)
Original Excel file with color-coded columns indicating units.

### 2. **ml_ready_data.csv** (8.9 KB) ⭐
**Main file for ML modeling** - Clean, properly formatted dataset ready for machine learning.

### 3. **data_dictionary.csv** (1.8 KB)
Complete metadata for all columns including units, types, and descriptions.

---

## 📊 Dataset Overview

- **Rows**: 22 observations
- **Columns**: 29 features
- **Time Period**: 2020 Q1 - 2025 Q2
- **Frequency**: Quarterly data
- **Missing Values**: 0% (all rows complete)

---

## 🎯 Target Variable

**Column**: `Nağd_pul_kredit_satışı` (Cash Loan Sales)
- **Unit**: Million AZN
- **Mean**: 80,612.82 million AZN
- **Std Dev**: 32,218.08 million AZN
- **Min**: 15,709.38 million AZN
- **Max**: 126,285.41 million AZN

---

## 📋 Feature Categories

### Time Features (4 columns)
1. **Rüblər** - Period label (e.g., "2020 I")
2. **Year** - Extracted year (2020-2025)
3. **Quarter** - Extracted quarter (1-4)
4. **Time_Index** - Sequential counter (0-21)

### Economic Indicators - Million AZN (17 columns)
- GDP
- Dövlət_Gəlirləri (Government Revenue)
- Dövlət_Xərcləri (Government Expenditure)
- Əhalinin_nominal_gəlirləri (Population Nominal Income)
- Əhalinin_banklardakı_əmanətləri (Population Bank Deposits)
- Orta_aylıq_əməkhaqqı (Average Monthly Salary)
- Xarici_ticarət_dövriyyəsi (Foreign Trade Turnover)
- İxrac (Exports)
- İdxal (Imports)
- Pul_bazası (Money Supply)
- Tikinti-quraşdırma_işlərinə_sərf_edilmiş_vəsait (Construction Investment)
- İstehlak_xərcləri (Consumer Spending)
- Yaşayış_evlərinin_tikintisinə_yönəldilmiş_investisiyalar (Housing Investment)
- Mənzil_qiymətləri (Housing Prices)
- Müştərilərə_verilmiş_kreditlər (Total Loans to Customers)
- NPLs (Non-Performing Loans)

### Oil Price (1 column)
- **Oil_Price** - $/barrel (Brent crude)

### Financial Ratios - Percentage (6 columns)
- ROA (Return on Assets)
- ROE (Return on Equity)
- Net_Interest_Margin
- Efficiency_Ratio
- Loan-to-Deposit_Ratio
- Uçot_faiz_dərəcəsi (Discount Rate)

### Customer Metrics - Count (1 column)
- Müştəri_sayı (Number of Customers)

---

## 🔄 Data Transformations Applied

### 1. **Oil Price Conversion**
```
Original: Stored as ratio (0.05 - 0.19)
Transformed: Multiplied by 100 → $/barrel (4.99 - 19.30)
```

### 2. **Percentage Columns**
```
Original: Stored as ratio (0.00 - 1.00)
Transformed: Multiplied by 100 → Percentage (0% - 100%)
Applies to: ROA, ROE, Net_Interest_Margin, Efficiency_Ratio,
            Loan-to-Deposit_Ratio, Uçot_faiz_dərəcəsi
```

### 3. **Time Features**
```
Original: "2020 I", "2020 II", etc.
Extracted: Year (2020), Quarter (1), Time_Index (0)
```

### 4. **Data Cleaning**
- All columns converted to proper numeric types
- Empty rows removed
- UTF-8 encoding with BOM for proper character display

---

## 📈 Usage Example

### Python (pandas)
```python
import pandas as pd

# Load the data
df = pd.read_csv('data/ml_ready_data.csv')

# Separate features and target
X = df.drop(['Rüblər', 'Nağd_pul_kredit_satışı'], axis=1)
y = df['Nağd_pul_kredit_satışı']

# Time-based split (last 20% for testing)
split_idx = int(len(df) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]
```

### R
```r
# Load the data
df <- read.csv('data/ml_ready_data.csv')

# View structure
str(df)
summary(df)
```

---

## 🔍 Key Insights

### Strong Predictors (Correlation > 0.7)
1. **GDP** (r = +0.777) - Very strong positive correlation
2. **Oil_Price** (r = +0.764) - Very strong positive correlation
3. **Xarici_ticarət_dövriyyəsi** (r = +0.752) - Very strong positive correlation

### Negative Predictors
- **NPLs** (r = -0.604) - Strong negative correlation
- Higher non-performing loans associated with lower loan sales

### Multicollinearity Warning
GDP, Oil_Price, and Foreign Trade are highly correlated (r > 0.8)
- Consider using PCA or selecting one as primary feature
- Or use regularized models (Ridge/Lasso)

---

## 💡 Modeling Recommendations

### Suggested Models
1. **Linear Regression** - Baseline model
2. **Ridge/Lasso Regression** - Handle multicollinearity
3. **Random Forest** - Capture non-linear relationships
4. **XGBoost/LightGBM** - Best performance for tabular data
5. **Time Series Models** - ARIMA, Prophet (use Time_Index)

### Feature Engineering Ideas
1. **Lag features**: Previous quarter's loan sales
2. **Rolling averages**: 2-quarter, 4-quarter moving averages
3. **Growth rates**: Quarter-over-quarter % change
4. **Seasonality**: Quarter dummies (Q1, Q2, Q3, Q4)
5. **Economic ratios**: Export/Import ratio, Loan/Deposit ratio

### Validation Strategy
⚠️ **Use Time-Based Split Only** (not random split!)
- Training: First 70-80% of data
- Validation: Next 10-15%
- Test: Last 10-15%

Reason: Time series data has temporal dependencies

---

## 📞 Contact & Questions

For questions about the data or methodology, refer to:
- **Analysis Notebook**: `loan_analysis.ipynb`
- **Data Preparation Script**: `prepare_ml_data.py`

---

## 📝 Version History

**v1.0** (2025-11-01)
- Initial ML-ready dataset
- 22 complete observations
- 29 features with proper units
- All transformations applied
