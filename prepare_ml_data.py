#!/usr/bin/env python3
"""
Prepare ML-ready CSV file from raw Excel data
Transforms all columns to proper numeric format with correct units
"""

import pandas as pd
import numpy as np

# Load raw data
df = pd.read_excel('data/raw_data.xlsx')

# Clean column names
df.columns = df.columns.str.strip()

# Convert all columns except Rüblər to numeric
for col in df.columns:
    if col != 'Rüblər':
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Unit definitions (from Excel color coding)
min_manat_cols = ['GDP', 'Dövlət_Gəlirləri', 'Dövlət_Xərcləri', 'Əhalinin_nominal_gəlirləri',
                  'Əhalinin_banklardakı_əmanətləri', 'Orta_aylıq_əməkhaqqı', 'Xarici_ticarət_dövriyyəsi',
                  'İxrac', 'İdxal', 'Pul_bazası', 'Oil_Price', 'Tikinti-quraşdırma_işlərinə_sərf_edilmiş_vəsait',
                  'İstehlak_xərcləri', 'Yaşayış_evlərinin_tikintisinə_yönəldilmiş_investisiyalar',
                  'Mənzil_qiymətləri', 'Nağd_pul_kredit_satışı', 'Müştərilərə_verilmiş_kreditlər', 'NPLs']

faiz_cols = ['ROA', 'ROE', 'Net_Interest_Margin', 'Efficiency_Ratio', 'Loan-to-Deposit_Ratio', 'Uçot_faiz_dərəcəsi']

say_cols = ['Müştəri_sayı']

# Apply transformations for ML modeling
# Oil_Price: convert ratio to $/barrel
df['Oil_Price'] = df['Oil_Price'] * 100

# Percentage columns: convert 0-1 ratio to percentage (0-100)
for col in faiz_cols:
    if col in df.columns:
        df[col] = df[col] * 100

# Create a clean ML-ready dataset
ml_data = df.copy()

# Remove rows with missing Rüblər (these are completely empty rows)
ml_data = ml_data.dropna(subset=['Rüblər'])

# Create additional features for ML
# Parse quarter information from Rüblər column
def parse_quarter(rubler_str):
    """Parse '2020 I' -> (2020, 1)"""
    if pd.isna(rubler_str):
        return None, None
    parts = str(rubler_str).strip().split()
    if len(parts) != 2:
        return None, None

    year = int(parts[0])
    quarter_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4}
    quarter = quarter_map.get(parts[1], None)
    return year, quarter

# Extract year and quarter
ml_data['Year'] = ml_data['Rüblər'].apply(lambda x: parse_quarter(x)[0])
ml_data['Quarter'] = ml_data['Rüblər'].apply(lambda x: parse_quarter(x)[1])

# Create time index (sequential counter)
ml_data = ml_data.sort_values(['Year', 'Quarter'])
ml_data['Time_Index'] = range(len(ml_data))

# Reorder columns: Time features first, then target, then features
time_cols = ['Rüblər', 'Year', 'Quarter', 'Time_Index']
target_col = ['Nağd_pul_kredit_satışı']  # Target variable for prediction
feature_cols = [col for col in ml_data.columns if col not in time_cols + target_col]

# Final column order
final_columns = time_cols + target_col + feature_cols
ml_data = ml_data[final_columns]

# Save to CSV
output_path = 'data/ml_ready_data.csv'
ml_data.to_csv(output_path, index=False, encoding='utf-8-sig')

# Create data dictionary
data_dict = {
    'Column': [],
    'Unit': [],
    'Description': [],
    'Data_Type': []
}

for col in ml_data.columns:
    data_dict['Column'].append(col)

    # Determine unit
    if col in ['Rüblər']:
        unit = 'Period (YYYY Q)'
        dtype = 'Categorical'
    elif col in ['Year']:
        unit = 'Year'
        dtype = 'Integer'
    elif col in ['Quarter']:
        unit = 'Quarter (1-4)'
        dtype = 'Integer'
    elif col in ['Time_Index']:
        unit = 'Sequential Index'
        dtype = 'Integer'
    elif col == 'Oil_Price':
        unit = '$/barrel'
        dtype = 'Float'
    elif col in faiz_cols:
        unit = 'Percentage (%)'
        dtype = 'Float'
    elif col in say_cols:
        unit = 'Count'
        dtype = 'Integer'
    elif col in min_manat_cols:
        unit = 'Million AZN'
        dtype = 'Float'
    else:
        unit = 'Unknown'
        dtype = 'Float'

    data_dict['Unit'].append(unit)
    data_dict['Data_Type'].append(dtype)

    # Add description
    if col == 'Nağd_pul_kredit_satışı':
        desc = 'TARGET: Cash loan sales (to predict)'
    elif col == 'Time_Index':
        desc = 'Sequential time index for modeling'
    elif col == 'Oil_Price':
        desc = 'Oil price (Brent crude)'
    elif col == 'NPLs':
        desc = 'Non-Performing Loans'
    elif col == 'ROA':
        desc = 'Return on Assets'
    elif col == 'ROE':
        desc = 'Return on Equity'
    else:
        desc = col.replace('_', ' ')

    data_dict['Description'].append(desc)

dict_df = pd.DataFrame(data_dict)
dict_df.to_csv('data/data_dictionary.csv', index=False, encoding='utf-8-sig')

# Print summary
print("="*80)
print("ML DATA PREPARATION COMPLETE")
print("="*80)
print(f"\n✅ ML-ready data saved to: {output_path}")
print(f"✅ Data dictionary saved to: data/data_dictionary.csv")
print(f"\n📊 Dataset Shape: {ml_data.shape[0]} rows × {ml_data.shape[1]} columns")
print(f"\n📋 Column Categories:")
print(f"   • Time features: {len(time_cols)}")
print(f"   • Target variable: 1 (Nağd_pul_kredit_satışı)")
print(f"   • Feature columns: {len(feature_cols)}")
print(f"\n💰 Unit Distribution:")
print(f"   • Million AZN: {len(min_manat_cols)} columns")
print(f"   • Percentage: {len(faiz_cols)} columns")
print(f"   • Count: {len(say_cols)} column")
print(f"   • $/barrel: 1 column (Oil_Price)")
print(f"\n📈 Data Transformations Applied:")
print(f"   ✓ Oil_Price: converted to $/barrel (×100)")
print(f"   ✓ Percentage columns: converted to % scale (×100)")
print(f"   ✓ Year & Quarter: extracted from Rüblər")
print(f"   ✓ Time_Index: added sequential counter")
print(f"\n🎯 Target Variable: Nağd_pul_kredit_satışı (Cash loan sales)")
print(f"   • Unit: Million AZN")
print(f"   • Non-null values: {ml_data['Nağd_pul_kredit_satışı'].notna().sum()}")
print(f"   • Mean: {ml_data['Nağd_pul_kredit_satışı'].mean():,.2f} million AZN")
print(f"   • Std: {ml_data['Nağd_pul_kredit_satışı'].std():,.2f} million AZN")
print(f"\n📝 Missing Values:")
total_missing = ml_data.isnull().sum().sum()
total_cells = ml_data.shape[0] * ml_data.shape[1]
print(f"   • Total missing: {total_missing} / {total_cells} ({total_missing/total_cells*100:.1f}%)")
print(f"   • Complete rows: {ml_data.dropna().shape[0]}")

# Show first few rows
print(f"\n📋 Preview (first 5 rows):")
print(ml_data.head())

print("\n" + "="*80)
print("Ready for ML modeling!")
print("="*80)
