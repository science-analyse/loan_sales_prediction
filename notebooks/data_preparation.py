"""
Loan Sales Prediction - Data Preparation Script

This script handles:
1. Loading raw data from Excel
2. Data cleaning and preprocessing
3. Feature engineering
4. Converting to ML-ready format
5. Saving processed data for model training and visualization

Usage:
    python data_preparation.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def load_raw_data(data_path):
    """Load raw data from Excel file"""
    if not data_path.exists():
        raise FileNotFoundError(f"❌ Data file not found: {data_path}")

    print(f"📂 Loading data from: {data_path}")
    df = pd.read_excel(data_path)
    print(f"✅ Data loaded successfully")
    print(f"📊 Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")

    return df


def parse_quarter_column(df):
    """Parse Rüblər column to extract Year and Quarter"""
    print("📅 Parsing quarter information...")

    roman_to_int = {'I': 1, 'II': 2, 'III': 3, 'IV': 4}

    def parse_quarter(quarter_str):
        if pd.isna(quarter_str):
            return None, None

        parts = str(quarter_str).strip().split()
        if len(parts) != 2:
            return None, None

        year = int(parts[0])
        quarter_roman = parts[1].strip()
        quarter = roman_to_int.get(quarter_roman)

        return year, quarter

    df[['Year', 'Quarter']] = df['Rüblər'].apply(
        lambda x: pd.Series(parse_quarter(x))
    )

    print(f"✅ Quarter parsing completed")
    print(f"   Date Range: {df['Year'].min()}-Q{df['Quarter'].min()} to {df['Year'].max()}-Q{df['Quarter'].max()}\n")

    return df


def apply_data_transformations(df):
    """Apply necessary data transformations"""
    print("🔧 Applying data transformations...")

    # Convert NPLs from thousands to actual values
    df['NPLs'] = df['NPLs'] * 1000
    print("✅ NPLs converted from thousands to actual values")

    return df


def create_time_features(df):
    """Create time-based features"""
    print("⏰ Creating time-based features...")

    df['Time_Index'] = range(len(df))
    df['Quarter_Sin'] = np.sin(2 * np.pi * df['Quarter'] / 4)
    df['Quarter_Cos'] = np.cos(2 * np.pi * df['Quarter'] / 4)

    print("✅ Time features created:")
    print("   - Time_Index: Sequential time index")
    print("   - Quarter_Sin: Sine encoding of quarter")
    print("   - Quarter_Cos: Cosine encoding of quarter\n")

    return df


def check_data_quality(df):
    """Perform data quality checks"""
    print("🔍 Checking data quality...")

    # Check duplicates
    duplicates = df.duplicated().sum()
    print(f"   Duplicate rows: {duplicates}")
    if duplicates > 0:
        df = df.drop_duplicates()
        print(f"   ✅ Duplicates removed")

    # Check infinite values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    inf_count = np.isinf(df[numeric_cols].values).sum()
    print(f"   Infinite values: {inf_count}")
    if inf_count > 0:
        df = df.replace([np.inf, -np.inf], np.nan)
        print(f"   ✅ Infinite values replaced with NaN")

    # Check missing values
    missing_total = df.isnull().sum().sum()
    print(f"   Missing values: {missing_total}")

    print("✅ Data quality check completed\n")

    return df


def calculate_npl_percentage(df):
    """Calculate NPL percentage if not already present"""
    print("📊 Calculating NPL percentage...")

    if 'NPL_percentage' not in df.columns:
        df['NPL_percentage'] = (df['NPLs'] / df['Portfel']) * 100
        print("✅ NPL_percentage calculated: (NPLs / Portfel) × 100\n")
    else:
        print("✅ NPL_percentage already exists\n")

    return df


def save_processed_data(df, output_paths):
    """Save processed data to multiple locations"""
    print("💾 Saving processed data...")

    saved_count = 0
    for path in output_paths:
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save CSV
        df.to_csv(path, index=False)
        print(f"✅ Saved to: {path}")
        saved_count += 1

    print(f"\n📊 Final Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"💾 Saved to {saved_count} location(s)\n")


def generate_summary_report(df, df_raw):
    """Generate and display summary report"""
    print("=" * 80)
    print("DATA PREPARATION SUMMARY REPORT")
    print("=" * 80)

    print("\n📊 DATASET OVERVIEW:")
    print(f"   Original Shape: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
    print(f"   Final Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"   New Features: {df.shape[1] - df_raw.shape[1]}")

    print("\n📅 TIME PERIOD:")
    print(f"   Start: {df['Year'].min()}-Q{df['Quarter'].min()}")
    print(f"   End: {df['Year'].max()}-Q{df['Quarter'].max()}")
    print(f"   Total Quarters: {len(df[df['Year'].notna()])}")

    print("\n📈 TARGET VARIABLE (Nağd_pul_kredit_satışı):")
    target_col = 'Nağd_pul_kredit_satışı'
    if target_col in df.columns:
        valid_target = df[df[target_col].notna()][target_col]
        print(f"   Valid Records: {len(valid_target)}")
        print(f"   Mean: {valid_target.mean():,.2f} AZN")
        print(f"   Std Dev: {valid_target.std():,.2f} AZN")
        print(f"   Min: {valid_target.min():,.2f} AZN")
        print(f"   Max: {valid_target.max():,.2f} AZN")

    print("\n🔧 FEATURES:")
    print(f"   Original Features: {len(df_raw.columns)}")
    print(f"   Time Features: 5 (Year, Quarter, Time_Index, Quarter_Sin, Quarter_Cos)")
    print(f"   Total Features: {len(df.columns)}")

    print("\n📊 KEY METRICS:")
    if 'NPL_percentage' in df.columns:
        npl_valid = df[df['NPL_percentage'].notna()]['NPL_percentage']
        print(f"   NPL Percentage: {npl_valid.mean():.2f}% (avg)")
    if 'ROE' in df.columns:
        roe_valid = df[df['ROE'].notna()]['ROE']
        print(f"   ROE: {roe_valid.mean()*100:.2f}% (avg)")
    if 'Müştəri_sayı' in df.columns:
        cust_valid = df[df['Müştəri_sayı'].notna()]['Müştəri_sayı']
        print(f"   Customers: {cust_valid.mean():,.0f} (avg)")

    print("\n" + "=" * 80)
    print("✅ DATA PREPARATION COMPLETE")
    print("=" * 80)


def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("LOAN SALES PREDICTION - DATA PREPARATION")
    print("=" * 80 + "\n")

    # Define paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_PATH = DATA_DIR / 'loan_sales.xlsx'

    # Output path - only save to notebooks/data directory
    output_paths = [
        DATA_DIR / 'ml_ready_data.csv'
    ]

    try:
        # Step 1: Load raw data
        df_raw = load_raw_data(RAW_DATA_PATH)

        # Step 2: Create working copy
        df = df_raw.copy()

        # Step 3: Parse quarter information
        df = parse_quarter_column(df)

        # Step 4: Apply data transformations
        df = apply_data_transformations(df)

        # Step 5: Calculate NPL percentage
        df = calculate_npl_percentage(df)

        # Step 6: Create time features
        df = create_time_features(df)

        # Step 7: Quality checks
        df = check_data_quality(df)

        # Step 8: Save processed data
        save_processed_data(df, output_paths)

        # Step 9: Generate summary report
        generate_summary_report(df, df_raw)

        return df

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise


if __name__ == "__main__":
    df_processed = main()
