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

        # Performans qiymətləndirməsi
        cv = (std_val / mean_val) * 100
        performance_rating = "Əla" if artım_faiz and artım_faiz > 10 else "Yaxşı" if artım_faiz and artım_faiz > 5 else "Orta" if artım_faiz and artım_faiz > 0 else "Zəif"

        # Kritik məlumat nöqtələri
        critical_insights = []
        if artım_faiz and artım_faiz > 15:
            critical_insights.append("🎉 Möhtəşəm artım! Son rübdə çox yüksək performans")
        elif artım_faiz and artım_faiz < -10:
            critical_insights.append("⚠️ DİQQƏT: Əhəmiyyətli azalma müşahidə olunur")

        if cv > 25:
            critical_insights.append("📊 Yüksək dəyişkənlik - planlaşdırma çətinliyi")

        if illik_artım and illik_artım > 20:
            critical_insights.append("📈 Güclü illik artım trendidir")

        return {
            "panel_haqqında": {
                "təsvir": "Bu panel biznesinizin sağlamlığını bir baxışda göstərir",
                "istifadə_təlimatı": "Hər göstəriciəyi diqqətlə nəzərdən keçirin və tendensiyaları izləyin",
                "yenilənmə_tezliyi": "Real-vaxt məlumatlar",
                "əhəmiyyəti": "Sürətli qərar qəbul etmək üçün ən vacib rəqəmlər buradadır"
            },
            "əsas_göstəricilər": {
                "son_dövr": {
                    "dövr": son_dövr['Rüblər'],
                    "dəyər": float(son_dövr[target]),
                    "vahid": "min manat",
                    "artım": float(artım) if artım is not None else None,
                    "artım_faiz": round(float(artım_faiz), 2) if artım_faiz is not None else None,
                    "status": "📈 Artım" if artım and artım > 0 else "📉 Azalma" if artım and artım < 0 else "➡️ Sabit",
                    "performans_reytinqi": performance_rating,
                    "izah": f"Əvvəlki rüblə nisbətən {abs(round(float(artım_faiz), 2)) if artım_faiz else 0}% dəyişiklik"
                },
                "ortalama_dəyər": {
                    "dəyər": round(float(mean_val), 2),
                    "təsvir": "Bütün dövrlərin ortalama dəyəri",
                    "praktik_mənа": "Gələcək hədəfləri təyin edərkən bu rəqəm baza ola bilər",
                    "son_dövrlə_müqayisə": round(float((son_dövr[target] - mean_val) / mean_val * 100), 2)
                },
                "median_dəyər": {
                    "dəyər": round(float(median_val), 2),
                    "təsvir": "Orta dəyər (50% aşağı, 50% yuxarı)",
                    "niyə_vacib": "Kənar dəyərlərdən təsirlənmir, daha etibarlı göstəricidir",
                    "ortalama_ilə_fərq": round(float(mean_val - median_val), 2)
                },
                "dəyişkənlik": {
                    "standart_sapma": round(float(std_val), 2),
                    "variasiya_əmsalı": round(cv, 2),
                    "təsvir": "Məlumatların nə qədər dəyişdiyini göstərir",
                    "qiymətləndirmə": "Stabil" if cv < 15 else "Orta dəyişkən" if cv < 25 else "Çox dəyişkən",
                    "praktik_nəticə": "Aşağı CV planlaşdırmanı asanlaşdırır" if cv < 15 else "Yüksək CV risk idarəetməsi tələb edir"
                }
            },
            "diapazon": {
                "minimum": {
                    "dəyər": float(y.min()),
                    "dövr": df.loc[y.idxmin(), 'Rüblər'],
                    "ortalamadan_nə_qədər_aşağı": round(float((mean_val - y.min()) / mean_val * 100), 2),
                    "qeyd": "Bu ən pis performans dövr üdür - səbəblərini araşdırın"
                },
                "maksimum": {
                    "dəyər": float(y.max()),
                    "dövr": df.loc[y.idxmax(), 'Rüblər'],
                    "ortalamadan_nə_qədər_yuxarı": round(float((y.max() - mean_val) / mean_val * 100), 2),
                    "qeyd": "Bu ən yaxşı performans dövrüdür - uğur faktorlarını təkrarlayın"
                },
                "fərq": float(y.max() - y.min()),
                "faiz_fərq": round(float((y.max() - y.min()) / y.min() * 100), 2),
                "mənası": "Minimum və maksimum arasındakı böyük fərq qeyri-sabitliyi göstərir"
            },
            "illik_müqayisə": {
                "cari_il": int(cari_il),
                "cari_il_ortalama": round(float(cari_il_data.mean()), 2) if len(cari_il_data) > 0 else None,
                "keçən_il": int(keçən_il),
                "keçən_il_ortalama": round(float(keçən_il_data.mean()), 2) if len(keçən_il_data) > 0 else None,
                "illik_artım_faiz": round(float(illik_artım), 2) if illik_artım is not None else None,
                "qiymətləndirmə": "Əla artım" if illik_artım and illik_artım > 15 else "Yaxşı artım" if illik_artım and illik_artım > 5 else "Zəif artım" if illik_artım and illik_artım > 0 else "Azalma - təcili müdaxilə lazım",
                "təklif": "Bu artım tempini saxlayın və daha da yüksəldin" if illik_artım and illik_artım > 0 else "Azalma səbəblərini araşdırın və strategiya dəyişdirin"
            },
            "tendensiya": {
                "qısamüddətli": "📈 Artım tendensiyası" if artım and artım > 0 else "📉 Azalma tendensiyası",
                "illik": "📈 İllik artım" if illik_artım and illik_artım > 0 else "📉 İllik azalma" if illik_artım else "Məlumat yoxdur",
                "gələcək_proqnoz": "Müsbət" if (artım and artım > 0) and (illik_artım and illik_artım > 0) else "Diqqət tələb edir",
                "tövsiyə": "Cari strategiyanı davam etdirin" if artım and artım > 0 else "Strategiyanı yenidən nəzərdən keçirin"
            },
            "kritik_məlumatlar": critical_insights if critical_insights else ["✅ Normal performans davam edir"],
            "növbəti_addımlar": {
                "təcili": "Azalma varsa dərhal səbəblərini araşdırın" if artım and artım < 0 else "Cari trendi davam etdirin",
                "qısa_müddət": "Növbəti rübün hədəfini müəyyənləşdirin",
                "orta_müddət": "İllik planı yeniləyin və resursları bölüşdürün",
                "uzun_müddət": "3 illik strateji plan hazırlayın"
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
                    "parametrik_testlər": bool(shapiro_p > 0.05),
                    "transformasiya_lazımdır": bool(shapiro_p <= 0.05),
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
                "trend_mövcudluğu": bool(p_value < 0.05),
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
        seasonality_strength = {}
        for q, data in quarterly_data.items():
            if data['ortalama']:
                idx = round((data['ortalama'] / overall_mean) * 100, 2)
                seasonal_indices[q] = idx
                # Mövsümiliyin gücünü hesabla
                deviation = abs(idx - 100)
                seasonality_strength[q] = "Çox güclü" if deviation > 20 else "Güclü" if deviation > 10 else "Orta" if deviation > 5 else "Zəif"

        return {
            "rüb_təhlili_nədir": {
                "təsvir": "Rüblər üzrə təhlil hər  rübün performansını  müqayisə edir və mövsümi nümunələri aşkar edir",
                "əhəmiyyəti": [
                    "Mövsümilik nümunələrini başa düşmək",
                    "Hər rüb üçün xüsusi strategiyalar hazırlamaq",
                    "Resursları düzgün bölüşdürmək",
                    "Gələcək rübləri daha yaxşı planlaşdırmaq"
                ],
                "istifadə_yolları": "Marketinq planlaması, Kadr idarəetməsi, Büdcə bölgüsü, İnventoriya idarəetməsi"
            },
            "rüblər_üzrə_statistika": quarterly_data,
            "müqayisəli_təhlil": {
                "ən_yaxşı_rüb": {
                    "rüb": best_quarter,
                    "ortalama": round(avg_values[best_quarter], 2) if best_quarter else None,
                    "mövsümilik_indeksi": seasonal_indices.get(best_quarter),
                    "ortalamadan_fərq": f"+{round(seasonal_indices.get(best_quarter, 100) - 100, 2)}%" if best_quarter else None,
                    "səbəblər": [
                        "Mövsümi amillər (Bayram, tətil sonrası)",
                        "İqtisadi dövriyyə (İldə bu dövr daha aktiv)",
                        "İstehlakçı davranışı (Alış gücünün yüksək olması)",
                        "Marketinq kampaniyalarının effektivliyi"
                    ],
                    "fəaliyyət_planı": [
                        f"Bu rübdə marketinq büdcəsini 20-30% artırın",
                        "Kadr sayını əvvəlcədən artırın",
                        "İnventoriya ehtiyatlarını vaxtından əvvəl hazırlayın",
                        "Xüsusi kampaniyalar və endirimlər planlaşdırın"
                    ]
                },
                "ən_zəif_rüb": {
                    "rüb": worst_quarter,
                    "ortalama": round(avg_values[worst_quarter], 2) if worst_quarter else None,
                    "mövsümilik_indeksi": seasonal_indices.get(worst_quarter),
                    "ortalamadan_fərq": f"{round(seasonal_indices.get(worst_quarter, 100) - 100, 2)}%" if worst_quarter else None,
                    "səbəblər": [
                        "Bayram dövrü və ya tətil ayları",
                        "Büdcə məhdudiyyətləri (müştərilərin pul sıxıntısı)",
                        "Mövsümi tələb azalması",
                        "Rəqabətin artması"
                    ],
                    "təkmilləşdirmə_strategiyaları": [
                        f"{worst_quarter} üçün xüsusi təşviq proqramları yaradın",
                        "Bu rübə öncədən hazırlıq: 2-3 ay əvvəl kampaniya planlaşdırın",
                        "Xərcləri optimize edin - lazımsız xərcləri kəsin",
                        "Müştəri loyallığı proqramları ilə tələbi stimullaşdırın",
                        "Endirim və bonuslarla satışı canlandırın"
                    ]
                },
                "fərq_təhlili": {
                    "mütləq_fərq": round(avg_values[best_quarter] - avg_values[worst_quarter], 2) if best_quarter and worst_quarter else None,
                    "faiz_fərq": round(((avg_values[best_quarter] - avg_values[worst_quarter]) / avg_values[worst_quarter]) * 100, 2) if best_quarter and worst_quarter else None,
                    "mənası": "Böyük fərq güclü mövsümiliyi göstərir - planlaşdırma zamanı nəzərə alın",
                    "risk": "Zəif rüblərdə cash flow problemləri yarana bilər" if best_quarter and worst_quarter and ((avg_values[best_quarter] - avg_values[worst_quarter]) / avg_values[worst_quarter] * 100) > 30 else "Fərq normal səviyyədədir"
                }
            },
            "mövsümilik_indeksi": {
                "izah": "100 = ortalama səviyyə. 100-dən yuxarı = güclü rüb, 100-dən aşağı = zəif rüb",
                "necə_hesablanır": "Rübün ortalaması / Ümumi ortalama × 100",
                "indekslər": seasonal_indices,
                "mövsümiliyin_gücü": seasonality_strength,
                "praktik_mənа": {
                    q: {
                        "status": "Güclü mövsüm" if idx > 110 else "Orta mövsüm" if idx > 95 else "Zəif mövsüm",
                        "tövsiyə": f"Bu rübdə aqressiv strategiya - resursları maksimum səfərbər edin" if idx > 110 else f"Bu rübdə müdafiə strategiyası - xərcləri nəzarətdə saxlayın" if idx < 95 else "Balanslaşdırılmış yanaşma"
                    }
                    for q, idx in seasonal_indices.items()
                }
            },
            "hər_rüb_üçün_xüsusi_plan": {
                "Q1": {
                    "xarakteristika": "İlin başlanğıcı, yeni büdcələr, planlaşdırma dövrü",
                    "gözlənilən_performans": "Orta səviyyə",
                    "kritik_amillər": ["Yeni il sonrası alış gücünün bərpası", "Büdcələrin ayrılması", "İllik planların həyata keçməsi"],
                    "fırsətlər": ["Yeni məhsul lansmanları", "İllik müqavilələr", "Strateji tərəfdaşlıqlar"],
                    "riskl ər": ["İstehlakçıların ehtiyatlı olması", "İqtisadi qeyri-müəyyənlik"],
                    "fəaliyyətlər": [
                        "İlin əvvəlində agr essiv marketinq",
                        "Yeni müştəri cəlb etmə kampaniyaları",
                        "Sadiq müştərilər üçün xüsusi təkliflər",
                        "KPI və hədəflərin təyin edilməsi"
                    ]
                },
                "Q2": {
                    "xarakteristika": "Bahar dövrü, artan iqtisadi fəaliyyət, pozitiv əhval-ruhiyyə",
                    "gözlənilən_performans": "Yüksələn trend",
                    "kritik_amillər": ["Bahar təmizliyi, yeniləmələr", "Artan istehlakçı etibarı", "İqtisadi canlanma"],
                    "fırsətlər": ["Mövsümi kampaniyalar", "Yeni bazar seqmentləri", "Genişlənmə"],
                    "risklər": ["Rəqabətin güclənməsi"],
                    "fəaliyyətlər": [
                        "Momentumdan yararlanın - artımı sürətləndirin",
                        "Yeni xidmət və ya məhsulları təqdim edin",
                        "Bazar payını artırmaq üçün investisiyalar",
                        "Müştəri bazasını genişləndirin"
                    ]
                },
                "Q3": {
                    "xarakteristika": "Yay dövrü, tətil mövsümü, dəyişkən performans",
                    "gözlənilən_performans": "Dəyişkən - mövsümdən asılı",
                    "kritik_amillər": ["Tətil planları", "Müştərilərin şəhərdən çıxması", "Yay ləngimələr i"],
                    "fırsətlər": ["Tətillə bağlı xidmətlər", "Onlayn satışların artması"],
                    "risklər": ["Tələbin azalması", "Kadr çatışmazlığı"],
                    "fəaliyyətlər": [
                        "Tətil dövrü təklifləri",
                        "Onlayn kanalları gücləndirin",
                        "Loyallıq proqramlarını aktivləşdirin",
                        "Payızafəaliyyətə hazırlıq başladın"
                    ]
                },
                "Q4": {
                    "xarakteristika": "İlin sonu, büdcə bitməsi, yeni il, yüksək aktivlik",
                    "gözlənilən_performans": "Ən yüksək fəaliyyət dövrü",
                    "kritik_amillər": ["İllik büdcələrin bitməsi", "Yeni il hədiyyələri", "İllik hədəflərə çatma təzyiqi"],
                    "fırsətlər": ["Qara Cümə, Yeni il kampaniyaları", "İllik yekunlaşdırma təklifləri", "Toplu satışlar"],
                    "risklər": ["Həddindən artıq rəqabət", "Tədarük çətinlikləri"],
                    "fəaliyyətlər": [
                        "Ən aqressiv marketinq dövrü",
                        "Stok və təchizat zəncirini qabaqcadan hazırlayın",
                        "Müvəqqəti kadr artımı",
                        "İllik yekunlaşdırma bonusları və endirimlər",
                        "Növbəti ilin planlaşdırmasına başlayın"
                    ]
                }
            },
            "ümumi_strategiya": {
                "resurs_bölgüsü": {
                    "güclü_rüblər": "Marketinq və satış resurslarının 60%-i",
                    "zəif_rüblər": "Xərc optimallaşdırması və effektivlik",
                    "orta_rüblər": "Balanslaşdırılmış yanaşma"
                },
                "cash_flow_idarəetməsi": "Güclü rüblərdə qazanılan gəliri zəif rüblərin xərclərini ödəmək üçün planlaşdırın",
                "kadr_planlaması": "Güclü rüblərdə müvəqqəti kadr artımı, zəif rüblərdə kadr optimallaşdırması",
                "inventoriya": "Güclü rüblərdən 2 ay əvvəl inventoriya artırın"
            },
            "nəticələr_və_tövsiyələr": [
                f"Ən güclü rüb {best_quarter} - bu rübdə maksimum investisiya edin" if best_quarter else "Rüblər balanslaşdırılmışdır",
                f"Ən zəif rüb {worst_quarter} - xüsusi təkmilləşdirmə tədbirləri tələb olunur" if worst_quarter else "",
                "Hər rübün xüsusiyyətlərini nəzərə alaraq fərqli strategiyalar tətbiq edin",
                "Mövsümi nümunələri öyrənin və gələcək planlaşdırmada istifadə edin",
                "Rüblər arası fərqi azaltmaq üçün zəif rüblərdə xüsusi tədbirlər görün"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")
