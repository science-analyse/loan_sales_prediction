"""
Statistika Routes - Dərin Statistik Təhlillər
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler

from app.utils.data_loader import data_loader

router = APIRouter()

@router.get("/descriptive", response_model=Dict[str, Any])
async def get_descriptive_statistics(column: str = Query("Nağd_pul_kredit_satışı", description="Təhlil ediləcək sütun")):
    """
    📊 Təsviri Statistika

    Seçilmiş dəyişən üzrə bütün təsviri statistik göstəricilər
    """
    try:
        df = data_loader.df

        if column not in df.columns:
            raise HTTPException(status_code=404, detail=f"'{column}' sütunu tapılmadı")

        series = df[column]

        # Əsas statistika
        desc = series.describe()

        return {
            "dəyişən": column,
            "əsas_statistika": {
                "say": int(desc['count']),
                "ortalama": round(float(desc['mean']), 2),
                "standart_sapma": round(float(desc['std']), 2),
                "minimum": round(float(desc['min']), 2),
                "25%_quartile": round(float(desc['25%']), 2),
                "median_50%": round(float(desc['50%']), 2),
                "75%_quartile": round(float(desc['75%']), 2),
                "maksimum": round(float(desc['max']), 2)
            },
            "əlavə_göstəricilər": {
                "variasiya": round(float(series.var()), 2),
                "variasiya_əmsalı_%": round(float((series.std() / series.mean()) * 100), 2),
                "diapazon": round(float(series.max() - series.min()), 2),
                "IQR": round(float(desc['75%'] - desc['25%']), 2),
                "mod": round(float(series.mode()[0]), 2) if len(series.mode()) > 0 else None
            },
            "paylanma_xüsusiyyətləri": {
                "skewness": round(float(stats.skew(series)), 4),
                "kurtosis_fisher": round(float(stats.kurtosis(series)), 4),
                "kurtosis_pearson": round(float(stats.kurtosis(series, fisher=False)), 4)
            },
            "praktik_intervallar": {
                "1_sigma": {
                    "aşağı": round(float(desc['mean'] - desc['std']), 2),
                    "yuxarı": round(float(desc['mean'] + desc['std']), 2),
                    "təsvir": "~68% məlumat"
                },
                "2_sigma": {
                    "aşağı": round(float(desc['mean'] - 2*desc['std']), 2),
                    "yuxarı": round(float(desc['mean'] + 2*desc['std']), 2),
                    "təsvir": "~95% məlumat"
                },
                "3_sigma": {
                    "aşağı": round(float(desc['mean'] - 3*desc['std']), 2),
                    "yuxarı": round(float(desc['mean'] + 3*desc['std']), 2),
                    "təsvir": "~99.7% məlumat"
                }
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")

@router.get("/correlation", response_model=Dict[str, Any])
async def get_correlation_analysis():
    """
    🔗 Korrelyasiya Təhlili

    Dəyişənlər arası əlaqələrin təhlili
    """
    try:
        df = data_loader.df
        numeric_cols = data_loader.get_numeric_columns()

        # Korrelyasiya matrisi
        corr_matrix = df[numeric_cols].corr()

        # Hədəf dəyişənlə korrelyasiyalar
        target = 'Nağd_pul_kredit_satışı'
        if target in numeric_cols:
            target_corrs = corr_matrix[target].drop(target).sort_values(ascending=False)

            strong_positive = target_corrs[target_corrs > 0.7]
            strong_negative = target_corrs[target_corrs < -0.7]
            moderate = target_corrs[(target_corrs >= 0.3) & (target_corrs <= 0.7)]

        return {
            "korrelyasiya_nədir": {
                "izah": "İki dəyişən arasında xətti əlaqənin gücü və istiqaməti",
                "diapazon": "-1 ilə +1 arası",
                "təfsir": {
                    "+1": "Mükəmməl müsbət korrelyasiya",
                    "0": "Korrelyasiya yoxdur",
                    "-1": "Mükəmməl mənfi korrelyasiya"
                },
                "vacib_qeyd": "Korrelyasiya ≠ Səbəbiyyət! (Correlation ≠ Causation)"
            },
            "korrelyasiya_gücü_təsnifatı": {
                "çox_güclü": "|r| > 0.9",
                "güclü": "0.7 < |r| ≤ 0.9",
                "orta": "0.4 < |r| ≤ 0.7",
                "zəif": "0.2 < |r| ≤ 0.4",
                "çox_zəif": "|r| ≤ 0.2"
            },
            "hədəf_dəyişənlə_korrelyasiyalar": {
                "güclü_müsbət": {
                    col: {
                        "r": round(float(val), 4),
                        "izah": f"{col} artdıqca {target} da artır",
                        "güc": "Güclü"
                    }
                    for col, val in strong_positive.items()
                } if len(strong_positive) > 0 else "Tapılmadı",
                "güclü_mənfi": {
                    col: {
                        "r": round(float(val), 4),
                        "izah": f"{col} artdıqca {target} azalır",
                        "güc": "Güclü"
                    }
                    for col, val in strong_negative.items()
                } if len(strong_negative) > 0 else "Tapılmadı",
                "orta_əlaqə": {
                    col: {
                        "r": round(float(val), 4),
                        "qiymət": "Müsbət" if val > 0 else "Mənfi",
                        "güc": "Orta"
                    }
                    for col, val in moderate.items()
                } if len(moderate) > 0 else "Tapılmadı"
            },
            "tam_korrelyasiya_matrisi": {
                "sütunlar": numeric_cols,
                "matris": corr_matrix.round(4).to_dict()
            },
            "multicollinearity_yoxlanışı": {
                "izah": "Müstəqil dəyişənlər arasında yüksək korrelyasiya",
                "problem": "Model performansını və təfsirini çətinləşdirir",
                "sərhəd": "|r| > 0.8-0.9 problemlidir",
                "yüksək_korrelyasiyalar": [
                    {
                        "dəyişən_1": col1,
                        "dəyişən_2": col2,
                        "korrelyasiya": round(float(corr_matrix.loc[col1, col2]), 4),
                        "risk": "Yüksək multicollinearity riski"
                    }
                    for i, col1 in enumerate(numeric_cols)
                    for col2 in numeric_cols[i+1:]
                    if abs(corr_matrix.loc[col1, col2]) > 0.8
                ] or "Yüksək multicollinearity tapılmadı ✅"
            },
            "praktik_tövsiyələr": [
                "Yüksək korrelyasiyon modeldə istifadə üçün yaxşıdır",
                "Multicollinearity varsa, dəyişənlərdən birini çıxarın",
                "Korrelyasiya səbəbiyyət demək deyil - kontekst vacibdir",
                "Qeyri-xətti əlaqələr korrelyasiyada görünməz"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")

@router.get("/normality-tests", response_model=Dict[str, Any])
async def get_normality_tests(column: str = Query("Nağd_pul_kredit_satışı")):
    """
    🔬 Normallıq Testləri

    Məlumatların normal paylanıb-paylanmadığını yoxlayır
    """
    try:
        df = data_loader.df

        if column not in df.columns:
            raise HTTPException(status_code=404, detail=f"'{column}' sütunu tapılmadı")

        series = df[column].dropna()

        # Shapiro-Wilk testi
        shapiro_stat, shapiro_p = stats.shapiro(series)

        # D'Agostino-Pearson testi
        dagostino_stat, dagostino_p = stats.normaltest(series)

        # Anderson-Darling testi
        anderson_result = stats.anderson(series, dist='norm')

        # Kolmogorov-Smirnov testi
        ks_stat, ks_p = stats.kstest(series, 'norm', args=(series.mean(), series.std()))

        return {
            "normallıq_nədir": {
                "izah": "Məlumatların normal (Gaussian) paylanma ilə uyğunluğu",
                "niyə_vacib": [
                    "Bir çox statistik testlər normal paylanma fərz edir",
                    "Parametrik testlərin əsasıdır",
                    "Model fərziyyələri üçün lazımdır"
                ],
                "normal_paylanma_xüsusiyyətləri": {
                    "forma": "Zəng (bell) forması",
                    "simmetriya": "Mean = Median = Mode",
                    "68_95_99_7_qaydası": "68% ±1σ, 95% ±2σ, 99.7% ±3σ"
                }
            },
            "test_nəticələri": {
                "1_shapiro_wilk": {
                    "izah": "Kiçik örnəklər üçün ən güclü test (n < 50)",
                    "statistika": round(float(shapiro_stat), 6),
                    "p_value": round(float(shapiro_p), 6),
                    "H0": "Məlumatlar normal paylanmışdır",
                    "H1": "Normal paylanmamışdır",
                    "nəticə": "✅ Normal paylanma (H0 qəbul)" if shapiro_p > 0.05 else "❌ Normal DEYİL (H0 rədd)",
                    "əminlik_səviyyəsi": "95%"
                },
                "2_dagostino_pearson": {
                    "izah": "Skewness və Kurtosis-a əsaslanan test",
                    "statistika": round(float(dagostino_stat), 6),
                    "p_value": round(float(dagostino_p), 6),
                    "nəticə": "✅ Normal paylanma" if dagostino_p > 0.05 else "❌ Normal DEYİL",
                    "üstünlük": "Böyük örnəklər üçün yaxşıdır"
                },
                "3_anderson_darling": {
                    "izah": "Quyruqlara daha həssas test",
                    "statistika": round(float(anderson_result.statistic), 6),
                    "kritik_dəyərlər": {
                        "15%": round(float(anderson_result.critical_values[0]), 4),
                        "10%": round(float(anderson_result.critical_values[1]), 4),
                        "5%": round(float(anderson_result.critical_values[2]), 4),
                        "2.5%": round(float(anderson_result.critical_values[3]), 4),
                        "1%": round(float(anderson_result.critical_values[4]), 4)
                    },
                    "nəticə": "✅ Normal (5% səviyyəsində)" if anderson_result.statistic < anderson_result.critical_values[2]
                            else "❌ Normal deyil"
                },
                "4_kolmogorov_smirnov": {
                    "izah": "Empirik və nəzəri paylanmaları müqayisə edir",
                    "statistika": round(float(ks_stat), 6),
                    "p_value": round(float(ks_p), 6),
                    "nəticə": "✅ Normal paylanma" if ks_p > 0.05 else "❌ Normal DEYİL",
                    "qeyd": "Böyük örnəklərdə həssasdır"
                }
            },
            "ümumi_qərar": {
                "testlərin_razılaşması": sum([
                    shapiro_p > 0.05,
                    dagostino_p > 0.05,
                    anderson_result.statistic < anderson_result.critical_values[2],
                    ks_p > 0.05
                ]),
                "4_testdən_razı": f"{sum([shapiro_p > 0.05, dagostino_p > 0.05, anderson_result.statistic < anderson_result.critical_values[2], ks_p > 0.05])}/4",
                "qərar": "✅ NORMAL PAYLANMA" if sum([shapiro_p > 0.05, dagostino_p > 0.05]) >= 1
                       else "❌ NORMAL DEYİL",
                "əminlik": "Yüksək" if sum([shapiro_p > 0.05, dagostino_p > 0.05, ks_p > 0.05]) >= 2
                         else "Orta" if sum([shapiro_p > 0.05, dagostino_p > 0.05, ks_p > 0.05]) == 1
                         else "Aşağı"
            },
            "tövsiyələr": {
                "normal_olarsa": [
                    "Parametrik testlər istifadə edin (t-test, ANOVA)",
                    "Pearson korrelyasiyası uyğundur",
                    "Xətti reqressiya fərziyyələri ödənilir"
                ],
                "normal_olmazsa": [
                    "Qeyri-parametrik testlər istifadə edin",
                    "Spearman korrelyasiyası istifadə edin",
                    "Transformasiya tətbiq edin (log, Box-Cox, sqrt)",
                    "Robust metodlar istifadə edin"
                ],
                "transformasiya_seçimi": {
                    "sağa_əyilmiş": "Log və ya sqrt transformasiyası",
                    "sola_əyilmiş": "Kvadrat transformasiya",
                    "hər_ikisi": "Box-Cox transformasiyası (optimal λ tapır)"
                }
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")

@router.get("/hypothesis-testing", response_model=Dict[str, Any])
async def get_hypothesis_testing():
    """
    🧪 Fərziyyə Testləri

    Müxtəlif fərziyyələrin statistik yoxlanması
    """
    try:
        df = data_loader.df
        target = 'Nağd_pul_kredit_satışı'
        y = df[target]

        # Ortalama müəyyən dəyərə bərabərdir? (One-sample t-test)
        hypothesized_mean = 100000  # Fərziyyə ortalama
        t_stat, t_pvalue = stats.ttest_1samp(y, hypothesized_mean)

        # İllər arası fərq varmı?
        years = sorted(df['Year'].unique())
        if len(years) >= 2:
            year1_data = df[df['Year'] == years[-2]][target]
            year2_data = df[df['Year'] == years[-1]][target]

            # İki örnəkli t-test
            t2_stat, t2_pvalue = stats.ttest_ind(year1_data, year2_data)

            # Mann-Whitney U test (qeyri-parametrik alternativ)
            u_stat, u_pvalue = stats.mannwhitneyu(year1_data, year2_data, alternative='two-sided')

        # Rüblər arası fərq varmı? (ANOVA)
        quarters_data = [df[df['Quarter'] == q][target].values for q in [1, 2, 3, 4]]
        f_stat, f_pvalue = stats.f_oneway(*quarters_data)

        # Kruskal-Wallis (qeyri-parametrik ANOVA)
        h_stat, h_pvalue = stats.kruskal(*quarters_data)

        return {
            "fərziyyə_testi_nədir": {
                "izah": "Məlumat əsasında müəyyən bir fikrin (fərziyyənin) doğruluğunu yoxlayırıq",
                "addımlar": [
                    "1. Null fərziyyə (H0) və alternativ fərziyyə (H1) qoyuruq",
                    "2. Əhəmiyyətlilik səviyyəsi (α) seçirik (adətən 0.05)",
                    "3. Testi aparırıq və p-value alırıq",
                    "4. Qərar veririk: p < α olarsa H0 rədd edilir"
                ],
                "p_value_izahı": {
                    "mənası": "H0 doğru olduqda belə nəticə almaq ehtimalı",
                    "p_0_05": "Çox güman ki tesadüfi deyil, H0 rədd edilir",
                    "p_0_05_plus": "Tesadüfi ola bilər, H0 qəbul edilir"
                }
            },
            "testlər": {
                "1_ortalama_testi": {
                    "ad": "One-Sample t-test",
                    "H0": f"Ortalama = {hypothesized_mean:,}",
                    "H1": f"Ortalama ≠ {hypothesized_mean:,}",
                    "nəticə": {
                        "faktiki_ortalama": round(float(y.mean()), 2),
                        "fərziyyə_ortalama": hypothesized_mean,
                        "t_statistika": round(float(t_stat), 4),
                        "p_value": round(float(t_pvalue), 6),
                        "qərar": f"❌ H0 rədd edilir (Ortalama {hypothesized_mean:,}-dən fərqlidir)" if t_pvalue < 0.05
                               else f"✅ H0 qəbul edilir (Ortalama {hypothesized_mean:,}-ə yaxındır)"
                    }
                },
                "2_illər_müqayisəsi": {
                    "ad": "İki örnəkli t-test",
                    "H0": f"{years[-2]} və {years[-1]} illərin ortalaması bərabərdir",
                    "H1": "Ortalamalar fərqlidir",
                    "parametrik_test": {
                        "ad": "Independent t-test",
                        "t_statistika": round(float(t2_stat), 4),
                        "p_value": round(float(t2_pvalue), 6),
                        "qərar": "❌ İllər arasında əhəmiyyətli fərq VAR" if t2_pvalue < 0.05
                               else "✅ İllər arasında əhəmiyyətli fərq YOXDUR"
                    },
                    "qeyri_parametrik_test": {
                        "ad": "Mann-Whitney U test",
                        "u_statistika": round(float(u_stat), 4),
                        "p_value": round(float(u_pvalue), 6),
                        "qərar": "❌ Fərq VAR" if u_pvalue < 0.05 else "✅ Fərq YOXDUR",
                        "nə_vaxt": "Məlumatlar normal paylanmayanda"
                    },
                    "praktik_fərq": {
                        f"{years[-2]}_ortalama": round(float(year1_data.mean()), 2),
                        f"{years[-1]}_ortalama": round(float(year2_data.mean()), 2),
                        "fərq": round(float(year2_data.mean() - year1_data.mean()), 2),
                        "fərq_faiz": round(float(((year2_data.mean() - year1_data.mean()) / year1_data.mean()) * 100), 2)
                    }
                },
                "3_rüblər_müqayisəsi": {
                    "ad": "ANOVA (Analysis of Variance)",
                    "H0": "Bütün rüblərin ortalaması bərabərdir",
                    "H1": "Ən azı bir rüb fərqlidir",
                    "parametrik_ANOVA": {
                        "F_statistika": round(float(f_stat), 4),
                        "p_value": round(float(f_pvalue), 6),
                        "qərar": "❌ Rüblər arasında əhəmiyyətli fərq VAR" if f_pvalue < 0.05
                               else "✅ Rüblər arasında əhəmiyyətli fərq YOXDUR",
                        "nə_vaxt": "3+ qrup müqayisəsi, normal paylanma"
                    },
                    "qeyri_parametrik_Kruskal": {
                        "H_statistika": round(float(h_stat), 4),
                        "p_value": round(float(h_pvalue), 6),
                        "qərar": "❌ Fərq VAR" if h_pvalue < 0.05 else "✅ Fərq YOXDUR",
                        "nə_vaxt": "Normal paylanma yoxdursa"
                    },
                    "rüblər_üzrə_ortalamalar": {
                        f"Q{i+1}": round(float(q.mean()), 2)
                        for i, q in enumerate(quarters_data)
                    }
                }
            },
            "praktik_təfsir": {
                "statistik_əhəmiyyət_vs_praktik_əhəmiyyət": {
                    "fərq": "p < 0.05 statistik əhəmiyyətli deməkdir, amma praktik əhəmiyyətli olmaya bilər",
                    "nümunə": "1000-lik fərq statistik əhəmiyyətli ola bilər, amma biznes üçün kiçikdir",
                    "tövsiyə": "Həm p-value, həm də effekt ölçüsünə (effect size) baxın"
                },
                "səhv_növləri": {
                    "Tip_I_səhv": "H0 doğrudur, amma rədd edirik (False Positive)",
                    "Tip_II_səhv": "H0 səhvdir, amma qəbul edirik (False Negative)",
                    "α_səviyyəsi": "Tip I səhv ehtimalı (adətən 0.05)"
                }
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xəta: {str(e)}")
