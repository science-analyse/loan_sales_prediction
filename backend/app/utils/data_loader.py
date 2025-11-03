"""
Məlumat yükləmə və emal utilities
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class DataLoader:
    """Məlumatları yükləmək və emal etmək üçün sinif"""

    def __init__(self):
        # Məlumat faylının yolu
        # Try multiple paths for different deployment scenarios
        possible_paths = [
            # Analytics dashboard public data path (PREFERRED)
            Path(__file__).parent.parent.parent.parent / "analytics-dashboard" / "public" / "data" / "ml_ready_data.csv",
            # Docker container path (data copied to /app/notebooks/data/)
            Path("/app/notebooks/data/ml_ready_data.csv"),
            # Development path (from backend directory)
            Path(__file__).parent.parent.parent.parent / "notebooks" / "data" / "ml_ready_data.csv",
            # Alternative Docker path
            Path(__file__).parent.parent / "notebooks" / "data" / "ml_ready_data.csv",
        ]

        self.data_path = None
        for path in possible_paths:
            if path.exists():
                self.data_path = path
                break

        if self.data_path is None:
            # Set to first path for better error message
            self.data_path = possible_paths[0]

        self._df = None
        # Don't load data at init - lazy load when needed

    def _load_data(self):
        """Məlumatları yüklə"""
        if self._df is not None:
            return  # Already loaded

        print(f"🔍 Attempting to load data from: {self.data_path}")
        print(f"🔍 File exists: {self.data_path.exists()}")

        if not self.data_path.exists():
            # List directory contents for debugging
            import os
            print(f"❌ Data file not found: {self.data_path}")
            parent_dir = self.data_path.parent
            if parent_dir.exists():
                print(f"📂 Parent directory contents: {list(parent_dir.iterdir())}")
            else:
                print(f"📂 Parent directory does not exist: {parent_dir}")
                # Try to find where we are
                print(f"📂 Current working directory: {os.getcwd()}")
                print(f"📂 Files in /app: {list(Path('/app').iterdir()) if Path('/app').exists() else 'N/A'}")

            raise FileNotFoundError(
                f"Data file not found: {self.data_path}\n"
                f"Please ensure ml_ready_data.csv is in the notebooks/data/ directory"
            )

        try:
            self._df = pd.read_csv(self.data_path)
            print(f"✅ Məlumatlar uğurla yükləndi: {len(self._df)} sətir from {self.data_path}")
        except Exception as e:
            print(f"❌ Məlumat yükləmə xətası: {str(e)}")
            raise

    @property
    def df(self) -> pd.DataFrame:
        """DataFrame-ə giriş"""
        if self._df is None:
            self._load_data()
        return self._df.copy()

    def get_summary(self) -> Dict[str, Any]:
        """Məlumatlar haqqında ümumi məlumat"""
        df = self.df

        return {
            "ümumi_məlumat": {
                "sətir_sayı": len(df),
                "sütun_sayı": len(df.columns),
                "başlanğıc_dövrü": df['Rüblər'].iloc[0],
                "son_dövr": df['Rüblər'].iloc[-1],
                "il_aralığı": f"{df['Year'].min()} - {df['Year'].max()}",
                "məlumat_yüklənmə_tarixi": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "sütunlar": {
                "rəqəmsal": df.select_dtypes(include=[np.number]).columns.tolist(),
                "kateqorik": df.select_dtypes(exclude=[np.number]).columns.tolist()
            },
            "boş_dəyərlər": df.isnull().sum().to_dict(),
            "məlumat_növləri": df.dtypes.astype(str).to_dict()
        }

    def get_target_variable(self, column: str = 'Nağd_pul_kredit_satışı') -> pd.Series:
        """Hədəf dəyişəni al"""
        return self.df[column]

    def get_numeric_columns(self) -> List[str]:
        """Rəqəmsal sütunları al"""
        return self.df.select_dtypes(include=[np.number]).columns.tolist()

    def get_time_series_data(self, column: str = 'Nağd_pul_kredit_satışı') -> Dict[str, Any]:
        """Zaman seriyası məlumatları"""
        df = self.df

        return {
            "dövrlər": df['Rüblər'].tolist(),
            "dəyərlər": df[column].tolist(),
            "illər": df['Year'].tolist(),
            "rüblər": df['Quarter'].tolist(),
            "statistika": {
                "ortalama": float(df[column].mean()),
                "median": float(df[column].median()),
                "minimum": float(df[column].min()),
                "maksimum": float(df[column].max()),
                "standart_sapma": float(df[column].std())
            }
        }

    def get_quarterly_comparison(self, column: str = 'Nağd_pul_kredit_satışı') -> Dict[str, Any]:
        """Rüblər üzrə müqayisə"""
        df = self.df

        quarterly_stats = {}
        for quarter in [1, 2, 3, 4]:
            q_data = df[df['Quarter'] == quarter][column]
            quarterly_stats[f"Q{quarter}"] = {
                "ortalama": float(q_data.mean()) if len(q_data) > 0 else None,
                "median": float(q_data.median()) if len(q_data) > 0 else None,
                "minimum": float(q_data.min()) if len(q_data) > 0 else None,
                "maksimum": float(q_data.max()) if len(q_data) > 0 else None,
                "sayı": int(len(q_data))
            }

        return quarterly_stats

    def get_yearly_comparison(self, column: str = 'Nağd_pul_kredit_satışı') -> Dict[str, Any]:
        """İllər üzrə müqayisə"""
        df = self.df

        yearly_stats = {}
        for year in sorted(df['Year'].unique()):
            y_data = df[df['Year'] == year][column]
            yearly_stats[str(year)] = {
                "ortalama": float(y_data.mean()) if len(y_data) > 0 else None,
                "cəm": float(y_data.sum()) if len(y_data) > 0 else None,
                "rüb_sayı": int(len(y_data)),
                "artım_faizi": None  # Hesablanacaq
            }

        # Artım faizini hesabla
        years = sorted(yearly_stats.keys())
        for i in range(1, len(years)):
            prev_sum = yearly_stats[years[i-1]]["cəm"]
            curr_sum = yearly_stats[years[i]]["cəm"]
            if prev_sum and curr_sum and prev_sum > 0:
                growth = ((curr_sum - prev_sum) / prev_sum) * 100
                yearly_stats[years[i]]["artım_faizi"] = round(growth, 2)

        return yearly_stats

    def get_correlation_matrix(self, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Korrelyasiya matrisi"""
        df = self.df

        if columns is None:
            columns = self.get_numeric_columns()

        corr_matrix = df[columns].corr()

        return {
            "sütunlar": columns,
            "matris": corr_matrix.round(4).to_dict(),
            "matris_list": corr_matrix.round(4).values.tolist()
        }

    def get_outliers(self, column: str = 'Nağd_pul_kredit_satışı', method: str = 'iqr') -> Dict[str, Any]:
        """Outlier-ləri tap"""
        series = self.df[column]

        if method == 'iqr':
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr

            outliers_mask = (series < lower_fence) | (series > upper_fence)
            outliers = series[outliers_mask]

            return {
                "metod": "IQR",
                "parametrlər": {
                    "Q1": float(q1),
                    "Q3": float(q3),
                    "IQR": float(iqr),
                    "aşağı_sərhəd": float(lower_fence),
                    "yuxarı_sərhəd": float(upper_fence)
                },
                "outlier_sayı": int(len(outliers)),
                "outlier_dəyərlər": [
                    {
                        "dövr": self.df.loc[idx, 'Rüblər'],
                        "dəyər": float(val),
                        "mövqe": "yuxarı" if val > upper_fence else "aşağı"
                    }
                    for idx, val in outliers.items()
                ]
            }

        elif method == 'zscore':
            mean = series.mean()
            std = series.std()
            z_scores = np.abs((series - mean) / std)
            threshold = 3

            outliers_mask = z_scores > threshold
            outliers = series[outliers_mask]

            return {
                "metod": "Z-Score",
                "parametrlər": {
                    "ortalama": float(mean),
                    "standart_sapma": float(std),
                    "sərhəd": threshold
                },
                "outlier_sayı": int(len(outliers)),
                "outlier_dəyərlər": [
                    {
                        "dövr": self.df.loc[idx, 'Rüblər'],
                        "dəyər": float(val),
                        "z_score": float(z_scores[idx])
                    }
                    for idx, val in outliers.items()
                ]
            }

        return {}

# Singleton instance
data_loader = DataLoader()
