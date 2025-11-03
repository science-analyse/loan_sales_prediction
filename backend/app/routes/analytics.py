"""
Analitika Routes - Ətraflı Təhlillər Azərbaycan dilində
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime

from app.utils.data_loader import data_loader

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data():
    """
    📊 Əsas İdarəetmə Paneli Məlumatları

    Kredit satışı üzrə ümumi statistika və əsas göstəricilər
    """
    try:
        df = data_loader.df
        target = 'Nağd_pul_kredit_satışı'
        y = df[target]

        # Əsas statistika
        mean_val = y.mean()
        median_val = y.median()
        std_val = y.std()

        # Son dövr məlumatları
        son_dövr = df.iloc[-1]
        əvvəlki_dövr = df.iloc[-2] if len(df) > 1 else None

        # Artım hesablama
        artım = None
        artım_faiz = None
        if əvvəlki_dövr is not None:
            artım = son_dövr[target] - əvvəlki_dövr[target]
            artım_faiz = (artım / əvvəlki_dövr[target]) * 100

        # İllik statistika
        cari_il = df['Year'].max()
        keçən_il = cari_il - 1

        cari_il_data = df[df['Year'] == cari_il][target]
        keçən_il_data = df[df['Year'] == keçən_il][target]

        illik_artım = None
        if len(keçən_il_data) > 0 and len(cari_il_data) > 0:
            illik_artım = ((cari_il_data.mean() - keçən_il_data.mean()) / keçən_il_data.mean()) * 100

        return {
            "əsas_göstəricilər": {
                "son_dövr": {
                    "dövr": son_dövr['Rüblər'],
                    "dəyər": float(son_dövr[target]),
                    "artım": float(artım) if artım is not None else None,
                    "artım_faiz": round(float(artım_faiz), 2) if artım_faiz is not None else None,
                    "status": "📈 Artım" if artım and artım > 0 else "📉 Azalma" if artım and artım < 0 else "➡️ Sabit"
                },
                "ortalama_dəyər": {
                    "dəyər": round(float(mean_val), 2),
                    "təsvir": "Bütün dövrlərin ortalama dəyəri"
                },
                "median_dəyər": {
                    "dəyər": round(float(median_val), 2),
                    "təsvir": "Orta dəyər (50% aşağı, 50% yuxarı)"
                },
                "dəyişkənlik": {
                    "standart_sapma": round(float(std_val), 2),
                    "variasiya_əmsalı": round(float((std_val / mean_val) * 100), 2),
                    "təsvir": "Məlumatların nə qədər dəyişdiyini göstərir"
                }
            },
            "diapazon": {
                "minimum": {
                    "dəyər": float(y.min()),
                    "dövr": df.loc[y.idxmin(), 'Rüblər']
                },
                "maksimum": {
                    "dəyər": float(y.max()),
                    "dövr": df.loc[y.idxmax(), 'Rüblər']
                },
                "fərq": float(y.max() - y.min())
            },
            "illik_müqayisə": {
                "cari_il": int(cari_il),
                "cari_il_ortalama": round(float(cari_il_data.mean()), 2) if len(cari_il_data) > 0 else None,
                "keçən_il": int(keçən_il),
                "keçən_il_ortalama": round(float(keçən_il_data.mean()), 2) if len(keçən_il_data) > 0 else None,
                "illik_artım_faiz": round(float(illik_artım), 2) if illik_artım is not None else None
            },
            "tendensiya": {
                "qısamüddətli": "📈 Artım tendensiyası" if artım and artım > 0 else "📉 Azalma tendensiyası",
                "illik": "📈 İllik artım" if illik_artım and illik_artım > 0 else "📉 İllik azalma" if illik_artım else "Məlumat yoxdur"
            },
            "yenilənmə_tarixi": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")

@router.get("/detailed-statistics", response_model=Dict[str, Any])
async def get_detailed_statistics():
    """
    📈 Ətraflı Statistik Təhlil

    Bütün statistik göstəricilər və onların izahları
    """
    try:
        df = data_loader.df
        target = 'Nağd_pul_kredit_satışı'
        y = df[target]

        # Əsas statistika
        mean_val = y.mean()
        median_val = y.median()
        mode_val = y.mode()[0] if len(y.mode()) > 0 else None
        std_val = y.std()
        var_val = y.var()
        cv_val = (std_val / mean_val) * 100

        # Quartiles
        q1 = y.quantile(0.25)
        q2 = y.quantile(0.50)  # median
        q3 = y.quantile(0.75)
        iqr = q3 - q1

        # Skewness və Kurtosis
        skewness = stats.skew(y)
        kurt = stats.kurtosis(y, fisher=False)
        fisher_kurt = stats.kurtosis(y, fisher=True)

        # Normallıq testləri
        shapiro_stat, shapiro_p = stats.shapiro(y)

        return {
            "mərkəzi_tendensiya": {
                "ortalama": {
                    "dəyər": round(float(mean_val), 2),
                    "izah": "Bütün dəyərlərin cəminin sayına bölünməsi",
                    "istifadə": "Normal paylanmış məlumatlar üçün ən yaxşı mərkəz ölçüsü",
                    "həssaslıq": "Outlier-lərə çox həssasdır"
                },
                "median": {
                    "dəyər": round(float(median_val), 2),
                    "izah": "Məlumatları iki bərabər hissəyə bölən dəyər",
                    "istifadə": "Outlier-lər olduqda ortalamadan daha etibarlıdır",
                    "üstünlük": "Outlier-lərə davamlıdır"
                },
                "mod": {
                    "dəyər": round(float(mode_val), 2) if mode_val is not None else None,
                    "izah": "Ən çox təkrarlanan dəyər",
                    "qeyd": "Rəqəmsal məlumatlar üçün çox da informativ deyil"
                },
                "mean_vs_median": {
                    "fərq": round(float(mean_val - median_val), 2),
                    "fərq_faiz": round(float(abs(mean_val - median_val) / median_val * 100), 2),
                    "təfsir": "Simmetrik paylanma" if abs(mean_val - median_val) / median_val < 0.05
                             else "Sağa əyilmiş" if mean_val > median_val else "Sola əyilmiş"
                }
            },
            "yayılma_və_dəyişkənlik": {
                "standart_sapma": {
                    "dəyər": round(float(std_val), 2),
                    "izah": "Məlumatların ortalamadan orta uzaqlığı",
                    "praktik_interval": {
                        "aşağı": round(float(mean_val - std_val), 2),
                        "yuxarı": round(float(mean_val + std_val), 2),
                        "faiz": "~68% məlumat bu intervaldadır"
                    }
                },
                "variasiya": {
                    "dəyər": round(float(var_val), 2),
                    "izah": "Standart sapmanın kvadratı (σ²)",
                    "qeyd": "Riyazi hesablamalar üçün, amma təfsiri çətin"
                },
                "variasiya_əmsalı": {
                    "dəyər": round(float(cv_val), 2),
                    "vahid": "%",
                    "izah": "Nisbi dəyişkənlik (std/mean × 100)",
                    "qiymətləndirmə": "Aşağı dəyişkənlik (Stabil)" if cv_val < 15
                                    else "Orta dəyişkənlik" if cv_val < 30
                                    else "Yüksək dəyişkənlik (Qeyri-stabil)",
                    "üstünlük": "Müxtəlif ölçülü dəyişənləri müqayisə edə bilərik"
                },
                "diapazon": {
                    "minimum": round(float(y.min()), 2),
                    "maksimum": round(float(y.max()), 2),
                    "fərq": round(float(y.max() - y.min()), 2),
                    "fərq_faiz": round(float((y.max() - y.min()) / mean_val * 100), 2)
                }
            },
            "quartile_təhlili": {
                "Q1_25%": {
                    "dəyər": round(float(q1), 2),
                    "izah": "Məlumatların 25%-i bundan aşağıdır"
                },
                "Q2_50%_Median": {
                    "dəyər": round(float(q2), 2),
                    "izah": "Orta dəyər"
                },
                "Q3_75%": {
                    "dəyər": round(float(q3), 2),
                    "izah": "Məlumatların 75%-i bundan aşağıdır"
                },
                "IQR": {
                    "dəyər": round(float(iqr), 2),
                    "formula": "Q3 - Q1",
                    "izah": "Məlumatların orta 50%-nin yayılması",
                    "istifadə": "Outlier aşkarlanması üçün əsas göstərici"
                }
            },
            "paylanma_forması": {
                "skewness": {
                    "dəyər": round(float(skewness), 4),
                    "izah": "Paylanmanın simmetriyası",
                    "təfsir": "Təqribən simmetrik" if abs(skewness) < 0.5
                             else f"Orta əyrilik ({'sağa' if skewness > 0 else 'sola'})" if abs(skewness) < 1
                             else f"Güclü əyrilik ({'sağa' if skewness > 0 else 'sola'})",
                    "praktik_mənа": "Uzun sağ quyruq (yüksək dəyərli outlier-lər)" if skewness > 1
                                   else "Uzun sol quyruq (aşağı dəyərli outlier-lər)" if skewness < -1
                                   else "Normal paylanmaya yaxın"
                },
                "kurtosis": {
                    "pearson": round(float(kurt), 4),
                    "fisher": round(float(fisher_kurt), 4),
                    "izah": "Quyruqların ağırlığı və zirvənin sivriliyi",
                    "təfsir": "Mesokurtic (Normal)" if abs(fisher_kurt) < 0.5
                             else "Leptokurtic (Sivri zirvə, ağır quyruqlar)" if fisher_kurt > 0.5
                             else "Platykurtic (Yastı zirvə, yüngül quyruqlar)",
                    "risk": "Yüksək outlier riski" if fisher_kurt > 0.5
                           else "Aşağı outlier riski" if fisher_kurt < -0.5
                           else "Orta outlier riski"
                }
            },
            "normallıq_testləri": {
                "shapiro_wilk": {
                    "statistika": round(float(shapiro_stat), 6),
                    "p_value": round(float(shapiro_p), 6),
                    "nəticə": "Normal paylanma" if shapiro_p > 0.05 else "Normal DEYİL",
                    "əminlik_səviyyəsi": "95%",
                    "izah": "Kiçik örnəklər üçün ən etibarlı normallıq testi"
                },
                "tövsiyə": {
                    "parametrik_testlər": shapiro_p > 0.05,
                    "transformasiya_lazımdır": shapiro_p <= 0.05,
                    "təklif": "Parametrik testlər istifadə edilə bilər" if shapiro_p > 0.05
                            else "Log və ya Box-Cox transformasiyası tövsiyə olunur"
                }
            },
            "ümumi_qiymətləndirmə": {
                "məlumat_keyfiyyəti": "Yaxşı" if cv_val < 30 and abs(skewness) < 1 else "Orta" if cv_val < 50 else "Zəif",
                "stabillik": "Stabil" if cv_val < 15 else "Orta stabil" if cv_val < 30 else "Qeyri-stabil",
                "proqnozlaşdırıla_bilənlik": "Yüksək" if cv_val < 20 and abs(skewness) < 0.5 else "Orta" if cv_val < 40 else "Aşağı"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")

@router.get("/outlier-analysis", response_model=Dict[str, Any])
async def get_outlier_analysis():
    """
    🔍 Outlier (Kənar Dəyər) Təhlili

    İki metod ilə outlier aşkarlanması və təhlili
    """
    try:
        # IQR və Z-score metodları ilə outlier-ləri tap
        iqr_outliers = data_loader.get_outliers(method='iqr')
        zscore_outliers = data_loader.get_outliers(method='zscore')

        return {
            "ümumi_məlumat": {
                "outlier_nədir": "Digər məlumatlardan çox fərqli olan müşahidələr",
                "niyə_yaranır": [
                    "Təbii dəyişiklik (məs. COVİD-19 təsiri)",
                    "Ölçmə xətası",
                    "Məlumat daxil etmə səhvi"
                ],
                "niyə_vacibdir": "Outlier-lər model performansını ciddi şəkildə təsir edə bilər"
            },
            "IQR_metodu": {
                "izah": "Interquartile Range (IQR) əsaslı metod",
                "formula": {
                    "aşağı_sərhəd": "Q1 - 1.5 × IQR",
                    "yuxarı_sərhəd": "Q3 + 1.5 × IQR"
                },
                "üstünlüklər": [
                    "Sadədir və başa düşüləndir",
                    "Median-a əsaslanır (robust)",
                    "Box plot-da vizual olaraq görünür"
                ],
                "çatışmazlıqlar": [
                    "1.5 katsayısı ixtiyaridir",
                    "Multivariate outlier-ləri tutmur"
                ],
                "nəticələr": iqr_outliers
            },
            "Z_Score_metodu": {
                "izah": "Standart sapma əsaslı metod",
                "formula": "Z = (X - μ) / σ",
                "sərhəd": "|Z| > 3",
                "mənası": "Dəyər ortalamadan 3 standart sapma uzaqdadır",
                "üstünlüklər": [
                    "Statistik əsası var",
                    "Normal paylanma üçün yaxşıdır",
                    "Quantitative qiymət verir"
                ],
                "çatışmazlıqlar": [
                    "Normal paylanma fərz edir",
                    "Outlier-lərə həssasdır (ortalama və std-ni dəyişir)"
                ],
                "nəticələr": zscore_outliers
            },
            "müqayisə": {
                "IQR_outlier_sayı": iqr_outliers["outlier_sayı"],
                "ZScore_outlier_sayı": zscore_outliers["outlier_sayı"],
                "ümumi_outlier": "Hər iki metod eyni nəticə verir"
                                if iqr_outliers["outlier_sayı"] == zscore_outliers["outlier_sayı"]
                                else "Metodlar fərqli nəticələr verir"
            },
            "tövsiyələr": {
                "araşdır": "Outlier-lərin səbəbini müəyyənləşdirin",
                "yoxla": "Məlumat xətası olmadığını təsdiqləyin",
                "strategiyalar": [
                    {
                        "ad": "Silib (Removal)",
                        "nə_vaxt": "Yalnız məlumat xətası olarsa",
                        "risk": "Mühüm informasiya itə bilər"
                    },
                    {
                        "ad": "Saxla (Keep)",
                        "nə_vaxt": "Həqiqi hadisədirsə",
                        "tövsiyə": "Robust metodlar istifadə edin"
                    },
                    {
                        "ad": "Transform et",
                        "metodlar": ["Log transformasiya", "Winsorization", "Capping"],
                        "nə_vaxt": "Outlier-lər təbii, amma modeli pozur"
                    },
                    {
                        "ad": "Ayrıca təhlil",
                        "nə_vaxt": "Outlier-lər maraq doğurur",
                        "yanaşma": "İki model: outlier-li və outlier-siz"
                    }
                ]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")

@router.get("/trend-analysis", response_model=Dict[str, Any])
async def get_trend_analysis():
    """
    📈 Trend Təhlili

    Zamanla dəyişmə tendensiyalarının təhlili
    """
    try:
        df = data_loader.df
        target = 'Nağd_pul_kredit_satışı'
        y = df[target].values

        # Linear trend
        x = np.arange(len(y))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # Son 4 rüb tendensiyası
        son_4_rub = y[-4:] if len(y) >= 4 else y
        x_son = np.arange(len(son_4_rub))
        slope_son, intercept_son, r_son, p_son, _ = stats.linregress(x_son, son_4_rub)

        # İllik artım templəri
        yearly_growth = data_loader.get_yearly_comparison()

        return {
            "ümumi_trend": {
                "təsvir": "Bütün dövr üzrə trend təhlili",
                "trend_əmsalı": round(float(slope), 2),
                "trend_istiqaməti": "📈 Artım trendidir" if slope > 0 else "📉 Azalma trendidir" if slope < 0 else "➡️ Sabit trend",
                "güclülük": {
                    "R²": round(float(r_value ** 2), 4),
                    "p_value": round(float(p_value), 6),
                    "izah": "R² 1-ə yaxın olduqca trend güclüdür",
                    "əhəmiyyətlilik": "Statistik cəhətdən əhəmiyyətlidir" if p_value < 0.05 else "Əhəmiyyətli deyil"
                },
                "ortalama_rüblük_dəyişmə": round(float(slope), 2),
                "illik_təxmini_dəyişmə": round(float(slope * 4), 2)
            },
            "son_dövrün_trendi": {
                "təsvir": "Son 4 rübün trenди",
                "trend_əmsalı": round(float(slope_son), 2),
                "trend_istiqaməti": "📈 Artım" if slope_son > 0 else "📉 Azalma" if slope_son < 0 else "➡️ Sabit",
                "R²": round(float(r_son ** 2), 4),
                "müqayisə": {
                    "ümumi_trend_ilə_fərq": round(float(slope_son - slope), 2),
                    "yorum": "Son dövrdə trend güclənib" if abs(slope_son) > abs(slope)
                           else "Son dövrdə trend zəifləyib" if abs(slope_son) < abs(slope)
                           else "Trend stabil qalır"
                }
            },
            "illik_artım_templəri": yearly_growth,
            "proqnoz_potensialı": {
                "trend_mövcudluğu": p_value < 0.05,
                "trend_gücü": "Güclü" if r_value ** 2 > 0.7 else "Orta" if r_value ** 2 > 0.4 else "Zəif",
                "proqnozlaşdırıla_bilənlik": "Yüksək" if p_value < 0.05 and r_value ** 2 > 0.6 else "Orta" if p_value < 0.05 else "Aşağı",
                "tövsiyə": "Linear trend modeli istifadə edilə bilər" if r_value ** 2 > 0.6
                         else "Daha mürəkkəb modellər lazımdır"
            },
            "risk_qiymətləndirməsi": {
                "dəyişkənlik": "Yüksək dəyişkənlik olduğu üçün proqnozlarda ehtiyatlı olun"
                              if (y.std() / y.mean()) > 0.3 else "Dəyişkənlik qəbul edilə bilən səviyyədədir",
                "outlier_təsiri": "Outlier-lər trend təhlilinə təsir edə bilər",
                "struktural_dəyişikliklər": "COVİD-19 və digər böhranlar trendi pozmuş ola bilər"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")

@router.get("/quarterly-insights", response_model=Dict[str, Any])
async def get_quarterly_insights():
    """
    📅 Rüblər üzrə Dərin Təhlil

    Hər rübün xüsusiyyətləri və müqayisəli təhlil
    """
    try:
        quarterly_data = data_loader.get_quarterly_comparison()
        df = data_loader.df
        target = 'Nağd_pul_kredit_satışı'

        # Ən yaxşı və ən pis rüb
        avg_values = {q: data['ortalama'] for q, data in quarterly_data.items() if data['ortalama']}
        best_quarter = max(avg_values, key=avg_values.get) if avg_values else None
        worst_quarter = min(avg_values, key=avg_values.get) if avg_values else None

        # Mövsümilik indeksi
        overall_mean = df[target].mean()
        seasonal_indices = {}
        for q, data in quarterly_data.items():
            if data['ortalama']:
                seasonal_indices[q] = round((data['ortalama'] / overall_mean) * 100, 2)

        return {
            "rüblər_üzrə_statistika": quarterly_data,
            "müqayisəli_təhlil": {
                "ən_yaxşı_rüb": {
                    "rüb": best_quarter,
                    "ortalama": round(avg_values[best_quarter], 2) if best_quarter else None,
                    "səbəblər": "Mövsümi amillər, iqtisadi dövriyyə, istehlakçı davranışı"
                },
                "ən_zəif_rüb": {
                    "rüb": worst_quarter,
                    "ortalama": round(avg_values[worst_quarter], 2) if worst_quarter else None,
                    "səbəblər": "Bayram dövrü, büdcə məhdudiyyətləri, mövsümi təsirlər"
                },
                "fərq": {
                    "mütləq": round(avg_values[best_quarter] - avg_values[worst_quarter], 2) if best_quarter and worst_quarter else None,
                    "faiz": round(((avg_values[best_quarter] - avg_values[worst_quarter]) / avg_values[worst_quarter]) * 100, 2) if best_quarter and worst_quarter else None
                }
            },
            "mövsümilik_indeksi": {
                "izah": "100-dən yuxarı = ortalamadan yuxarı, 100-dən aşağı = ortalamadan aşağı",
                "indekslər": seasonal_indices,
                "praktik_mənа": {
                    q: "Güclü mövsüm" if idx > 110 else "Orta mövsüm" if idx > 95 else "Zəif mövsüm"
                    for q, idx in seasonal_indices.items()
                }
            },
            "nümunələr": {
                "Q1": {
                    "xüsusiyyətlər": "İlin başlanğıcı, yeni büdcələr, planlaşdırma",
                    "gözlənilən": "Orta səviyyə"
                },
                "Q2": {
                    "xüsusiyyətlər": "Bahar dövrü, artan iqtisadi fəaliyyət",
                    "gözlənilən": "Yüksələn trend"
                },
                "Q3": {
                    "xüsusiyyətlər": "Yay dövrü, tətil mövsümü",
                    "gözlənilən": "Dəyişkən"
                },
                "Q4": {
                    "xüsusiyyətlər": "İlin sonu, büdcə bitməsi, yeni il",
                    "gözlənilən": "Yüksək fəaliyyət"
                }
            },
            "biznes_tövsiyələri": [
                "Güclü rüblərdə marketinq kampaniyalarını artırın",
                "Zəif rüblərdə xərcləri optimallaşdırın",
                "Mövsümi nümunələrə uyğun kadr planlaması",
                "İnventoriya idarəetməsində mövsümilik nəzərə alınsın"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")
