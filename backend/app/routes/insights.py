"""
Təhlillər və İş Tövsiyələri Endpoint-ləri
Business Insights and Recommendations Routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime

from app.utils.data_loader import data_loader

router = APIRouter()


@router.get("/executive-summary", response_model=Dict[str, Any])
async def get_executive_summary():
    """
    📋 İcraçı İcmal

    Üst rəhbərlik üçün qısa və əhatəli məlumat
    Əsas rəqəmlər, tendensiyalar və tövsiyələr
    """
    df = data_loader.df
    y = df['Nağd_pul_kredit_satışı'].values

    # Əsas göstəricilər
    current_value = y[-1]
    previous_value = y[-2]
    yoy_previous = y[-5] if len(y) >= 5 else y[0]

    # Dəyişikliklər
    qoq_change = current_value - previous_value
    qoq_pct = (qoq_change / previous_value * 100) if previous_value != 0 else 0

    yoy_change = current_value - yoy_previous
    yoy_pct = (yoy_change / yoy_previous * 100) if yoy_previous != 0 else 0

    # Trend analizi (son 8 rüb)
    recent_trend = np.polyfit(range(8), y[-8:], 1)[0]
    trend_direction = "Artım" if recent_trend > 0 else "Azalma"

    # Volatility
    volatility = np.std(y[-8:]) / np.mean(y[-8:]) * 100

    # Growth rate (son 4 rüb vs əvvəlki 4 rüb)
    recent_avg = np.mean(y[-4:])
    previous_avg = np.mean(y[-8:-4]) if len(y) >= 8 else np.mean(y[:-4])
    growth_rate = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg != 0 else 0

    # Risk assessment
    if volatility < 10:
        risk_level = "Aşağı"
        risk_description = "Sabit və proqnozlaşdırıla bilən"
    elif volatility < 20:
        risk_level = "Orta"
        risk_description = "Qəbul edilə bilən dəyişkənlik"
    else:
        risk_level = "Yüksək"
        risk_description = "Yüksək dəyişkənlik, ehtiyatlı olun"

    # Key insights
    insights = []

    if qoq_pct > 5:
        insights.append({
            "tip": "Pozitiv",
            "başlıq": "Güclü Rüb-Rüb Artım",
            "məzmun": f"Son rübdə {qoq_pct:.1f}% artım müşahidə olunur ki, bu çox yaxşı göstəricidir",
            "prioritet": "Yüksək"
        })
    elif qoq_pct < -5:
        insights.append({
            "tip": "Diqqət",
            "başlıq": "Rüb-Rüb Azalma",
            "məzmun": f"Son rübdə {abs(qoq_pct):.1f}% azalma var. Səbəbləri araşdırın",
            "prioritet": "Yüksək"
        })

    if yoy_pct > 10:
        insights.append({
            "tip": "Pozitiv",
            "başlıq": "Əla İl-İl Artım",
            "məzmun": f"İl-il {yoy_pct:.1f}% artım sürətli inkişafı göstərir",
            "prioritet": "Orta"
        })
    elif yoy_pct < 0:
        insights.append({
            "tip": "Neqativ",
            "başlıq": "İl-İl Azalma",
            "məzmun": f"Keçən ilin eyni dövrü ilə müqayisədə {abs(yoy_pct):.1f}% azalma",
            "prioritet": "Yüksək"
        })

    if volatility > 20:
        insights.append({
            "tip": "Diqqət",
            "başlıq": "Yüksək Volatillik",
            "məzmun": f"Satışlar qeyri-sabiltdir (volatillik: {volatility:.1f}%). Risk idarəetməsi lazımdır",
            "prioritet": "Orta"
        })

    # Recommendations
    recommendations = []

    if trend_direction == "Artım":
        recommendations.append({
            "sahə": "Strateji Planlaşdırma",
            "tövsiyə": "Artım tendensiyası davam edir. Bazardan daha çox pay almaq üçün marketinq büdcəsini artırın",
            "gözlənilən_təsir": "Orta müddətdə 15-20% əlavə artım"
        })
    else:
        recommendations.append({
            "sahə": "Risk İdarəetməsi",
            "tövsiyə": "Azalma tendensiyası var. Müştəri saxlanması və yeni məhsullar üzərində işləyin",
            "gözlənilən_təsir": "Trendin dayanması və ya dönməsi"
        })

    if volatility > 15:
        recommendations.append({
            "sahə": "Maliyyə Planlaşdırma",
            "tövsiyə": "Yüksək volatillik səbəbilə ehtiyat fondunu artırın və cash flow idarəetməsini gücləndi rin",
            "gözlənilən_təsir": "Maliyyə sabitliyinin artması"
        })

    recommendations.append({
        "sahə": "Məlumat Analitikası",
        "tövsiyə": "Əlavə dəyişənlər (makroiqtisadi göstəricilər, müştəri davranışı) əlavə edərək proqnoz dəqiqliyini artırın",
        "gözlənilən_təsir": "Proqnoz xətasının 30-40% azalması"
    })

    return {
        "icmal_tarixi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dövr": df['Rüblər'].iloc[-1],
        "əsas_rəqəmlər": {
            "cari_dəyər": {
                "məbləğ": round(current_value, 2),
                "vahid": "min manat"
            },
            "rüb_rüb_dəyişiklik": {
                "məbləğ": round(qoq_change, 2),
                "faiz": round(qoq_pct, 2),
                "istiqamət": "Artım" if qoq_change > 0 else "Azalma",
                "qiymət": "Pozitiv" if qoq_pct > 0 else "Neqativ" if qoq_pct < -2 else "Neytral"
            },
            "il_il_dəyişiklik": {
                "məbləğ": round(yoy_change, 2),
                "faiz": round(yoy_pct, 2),
                "istiqamət": "Artım" if yoy_change > 0 else "Azalma",
                "qiymət": "Əla" if yoy_pct > 10 else "Yaxşı" if yoy_pct > 5 else "Zəif" if yoy_pct < 0 else "Orta"
            }
        },
        "tendensiya": {
            "istiqamət": trend_direction,
            "gücü": "Güclü" if abs(recent_trend) > 1000 else "Orta" if abs(recent_trend) > 500 else "Zəif",
            "rüb_başına_dəyişmə": round(recent_trend, 2),
            "il_proqnozu": round(recent_trend * 4, 2)
        },
        "risk_qiymətləndirməsi": {
            "səviyyə": risk_level,
            "volatillik": round(volatility, 2),
            "təsvir": risk_description,
            "məsləhət": "Ehtiyat fondunu artırın" if risk_level == "Yüksək" else "Cari strategiyanı davam etdirin"
        },
        "əsas_təhlillər": insights,
        "tövsiyələr": recommendations,
        "növbəti_addımlar": [
            "Əsas təhlilləri nəzərdən keçirin və prioritetləri müəyyənləşdirin",
            "Tövsiyələri komanda ilə müzakirə edin",
            "Hər tövsiyə üçün icra planı hazırlayın",
            "Proqnozları izləyin və real nəticələrlə müqayisə edin"
        ]
    }


@router.get("/performance-metrics", response_model=Dict[str, Any])
async def get_performance_metrics():
    """
    📊 Performans Göstəriciləri

    KPI-lər və performans ölçümləri
    Hədəflərə nəzərən faktiki nəticələr
    """
    df = data_loader.df
    y = df['Nağd_pul_kredit_satışı'].values
    years = df['Year'].values

    current_year = years[-1]
    current_quarter = df['Quarter'].iloc[-1]

    # İllik göstəricilər
    current_year_data = y[years == current_year]
    previous_year = current_year - 1
    previous_year_data = y[years == previous_year] if previous_year in years else np.array([])

    # YTD (Year-to-Date)
    ytd_total = np.sum(current_year_data)
    ytd_avg = np.mean(current_year_data)

    # Əvvəlki il eyni dövr
    if len(previous_year_data) >= len(current_year_data):
        pytd_total = np.sum(previous_year_data[:len(current_year_data)])
        ytd_growth = ((ytd_total - pytd_total) / pytd_total * 100) if pytd_total != 0 else 0
    else:
        pytd_total = None
        ytd_growth = None

    # Target setting (realistic based on historical data)
    historical_growth = np.mean([
        (y[i] - y[i-4]) / y[i-4] * 100
        for i in range(4, len(y))
        if i >= 4 and y[i-4] != 0
    ])

    target_quarterly = np.mean(y[-8:]) * (1 + historical_growth/100)
    target_annual = target_quarterly * 4

    # Performance against target
    current_value = y[-1]
    quarterly_achievement = (current_value / target_quarterly * 100) if target_quarterly != 0 else 0

    # Consistency score (lower CV = more consistent)
    cv = np.std(y) / np.mean(y) * 100
    consistency_score = max(0, 100 - cv)

    # Growth stability
    growth_rates = [(y[i] - y[i-1]) / y[i-1] * 100 for i in range(1, len(y)) if y[i-1] != 0]
    growth_std = np.std(growth_rates)

    if growth_std < 5:
        stability = "Çox Stabil"
    elif growth_std < 10:
        stability = "Stabil"
    elif growth_std < 20:
        stability = "Orta Stabil"
    else:
        stability = "Qeyri-stabil"

    # Market position (simulated - assuming total market)
    # Bu real məlumatlarda bazarın ümumi həcmi ilə müqayisə olmalıdır
    assumed_market_size = ytd_total * 5  # Fərziyyə: Biz bazarın 20%-ni tuturuq
    market_share = 20.0

    return {
        "performans_göstəriciləri_nədir": {
            "təsvir": "KPI (Key Performance Indicators) - Əsas Performans Göstəriciləri biznesin məqsədlərə nə dərəcədə çatdığını ölçür",
            "əhəmiyyəti": [
                "Uğur və uğursuzluğu obyektiv ölçmək",
                "Hədəflərə çatmaq üçün tənzimləmələr etmək",
                "Komandanı motivasiya etmək və hesabatlılıq",
                "Strategiyanı məlumat əsasında qərar vermək"
            ],
            "tez-tez_istifadə": "Hər rüb və ya aylıq performans icmalında"
        },
        "cari_performans": {
            "dövr": df['Rüblər'].iloc[-1],
            "faktiki_dəyər": round(current_value, 2),
            "hədəf": round(target_quarterly, 2),
            "nail_olma_faizi": round(quarterly_achievement, 2),
            "status": "Hədəf Aşıldı" if quarterly_achievement >= 100 else "Hədəfə Yaxın" if quarterly_achievement >= 90 else "Hədəfdən Uzaq",
            "fərq": round(current_value - target_quarterly, 2)
        },
        "illik_performans": {
            "il": int(current_year),
            "YTD_cəmi": round(ytd_total, 2),
            "YTD_ortalama": round(ytd_avg, 2),
            "keçmiş_il_YTD": round(pytd_total, 2) if pytd_total else "N/A",
            "artım_YTD": round(ytd_growth, 2) if ytd_growth else "N/A",
            "illik_hədəf": round(target_annual, 2),
            "proqnoz_nail_olma": round((ytd_total / target_annual * 100), 2),
            "qalan_rüblər": 4 - current_quarter,
            "rüb_başına_lazım_olan": round((target_annual - ytd_total) / (4 - current_quarter), 2) if current_quarter < 4 else 0
        },
        "sabitlik_göstəriciləri": {
            "ardıcıllıq_xalı": round(consistency_score, 2),
            "dəyişkənlik_əmsalı": round(cv, 2),
            "artım_sabitliyi": stability,
            "izah": "Yüksək ardıcıllıq xalı proqnozlaşdırmanı asanlaşdırır və planlaşdırma üçün yaxşıdır"
        },
        "bazar_mövqeyi": {
            "bazar_payı": f"{market_share}%",
            "qeyd": "Fərziyyə əsasında. Real bazar məlumatları ilə yeniləyin",
            "rəqabət_mövqeyi": "Güclü" if market_share > 20 else "Orta",
            "tövsiyə": "Bazar payını artırmaq üçün aqressiv marketinq strategiyası" if market_share < 25 else "Cari mövqeyi qorumaq"
        },
        "qiymətləndirmə": {
            "ümumi_qiymət": "Əla" if quarterly_achievement >= 100 and consistency_score > 80 else "Yaxşı" if quarterly_achievement >= 90 else "İnkişaf Lazımdır",
            "güclü_tərəflər": [
                item for item in [
                    "Hədəflərə nail olma" if quarterly_achievement >= 100 else None,
                    "Yüksək sabitlik" if consistency_score > 80 else None,
                    "Müsbət artım" if ytd_growth and ytd_growth > 0 else None
                ] if item
            ],
            "təkmilləşdirmə_sahələri": [
                item for item in [
                    "Hədəflərə çatma" if quarterly_achievement < 90 else None,
                    "Sabitliyin artırılması" if consistency_score < 70 else None,
                    "Artım tempinin yüksəldilməsi" if ytd_growth and ytd_growth < 5 else None
                ] if item
            ]
        }
    }


@router.get("/risk-analysis", response_model=Dict[str, Any])
async def get_risk_analysis():
    """
    ⚠️ Risk Təhlili

    Potensial risklər və onların idarə edilməsi
    """
    df = data_loader.df
    y = df['Nağd_pul_kredit_satışı'].values

    # Volatility risk
    volatility = np.std(y) / np.mean(y) * 100

    # Downside risk (values below mean)
    mean_val = np.mean(y)
    downside_values = y[y < mean_val]
    downside_vol = np.std(downside_values) / mean_val * 100 if len(downside_values) > 0 else 0

    # Trend reversal risk
    recent_trend = np.polyfit(range(8), y[-8:], 1)[0]
    older_trend = np.polyfit(range(8), y[-16:-8], 1)[0] if len(y) >= 16 else recent_trend
    trend_change = abs(recent_trend - older_trend) / abs(older_trend) * 100 if older_trend != 0 else 0

    # Concentration risk (quarterly)
    quarterly_dist = {}
    for q in range(1, 5):
        q_data = y[df['Quarter'] == q]
        quarterly_dist[f"Q{q}"] = np.sum(q_data) / np.sum(y) * 100 if len(q_data) > 0 else 0

    max_quarter_conc = max(quarterly_dist.values())

    # Value at Risk (VaR) - 95% confidence
    sorted_y = np.sort(y)
    var_95_index = int(len(sorted_y) * 0.05)
    var_95 = sorted_y[var_95_index]
    var_loss = mean_val - var_95

    # Risk classification
    risks = []

    if volatility > 20:
        risks.append({
            "tip": "Yüksək",
            "kateqoriya": "Volatillik Riski",
            "təsvir": f"Satışlar çox dəyişkəndir (CV: {volatility:.1f}%). Bu planlaşdırmanı çətinləşdirir",
            "təsir": "Yüksək",
            "ehtimal": "Yüksək",
            "azaldılması": [
                "Məhsul portfelini diversifikasiya edin",
                "Müştəri bazasını genişləndirin",
                "Mövsümilikdən asılı olmayan gəlir mənbələri yaradın"
            ]
        })
    elif volatility > 10:
        risks.append({
            "tip": "Orta",
            "kateqoriya": "Volatillik Riski",
            "təsvir": f"Orta səviyyəli dəyişkənlik (CV: {volatility:.1f}%)",
            "təsir": "Orta",
            "ehtimal": "Orta",
            "azaldılması": [
                "Mövcud müştəri saxlanmasına fokuslanın",
                "Proqnozlaşdırma modellərini təkmilləşdirin"
            ]
        })

    if recent_trend < 0:
        risks.append({
            "tip": "Yüksək",
            "kateqoriya": "Trend Riski",
            "təsvir": "Azalan trend müşahidə olunur. Bazar payı itirmə riski",
            "təsir": "Yüksək",
            "ehtimal": "Orta",
            "azaldılması": [
                "Rəqabət təhlili aparın",
                "Müştəri rəylərini toplayın və problemi müəyyənləşdirin",
                "Yeni marketinq kampaniyaları başladın",
                "Məhsul/xidmət keyfiyyətini yoxlayın"
            ]
        })

    if max_quarter_conc > 30:
        risks.append({
            "tip": "Orta",
            "kateqoriya": "Konsentrasiya Riski",
            "təsvir": f"Satışların çoxu bir rübdə cəmləşib ({max_quarter_conc:.1f}%). Bu mövsümi asılılıq yaradır",
            "təsir": "Orta",
            "ehtimal": "Yüksək",
            "azaldılması": [
                "Zəif rüblər üçün xüsusi təşviq proqramları",
                "İl boyu sabit gəlir təmin edən məhsullar əlavə edin",
                "Cash flow idarəetməsini gücləndir in"
            ]
        })

    if downside_vol > 15:
        risks.append({
            "tip": "Orta",
            "kateqoriya": "Aşağı Trend Riski",
            "təsvir": f"Ortalamadan aşağı dəyərlərdə yüksək variasiya ({downside_vol:.1f}%)",
            "təsir": "Orta",
            "ehtimal": "Orta",
            "azaldılması": [
                "Minimum performans hədəfləri müəyyənləşdirin",
                "Zəif dövrlərdə xüsusi tədbirlər planlaşdırın"
            ]
        })

    # Overall risk score
    risk_score = (
        (volatility / 30 * 30) +  # 30% weight
        (downside_vol / 20 * 20) +  # 20% weight
        (abs(recent_trend) < 500) * 20 +  # 20% if weak trend
        (max_quarter_conc > 30) * 15 +  # 15% concentration
        (trend_change > 50) * 15  # 15% trend instability
    )

    return {
        "risk_təhlili_nədir": {
            "təsvir": "Risk təhlili potensial problemləri əvvəlcədən müəyyənləşdirir və onların qarşısını almaq üçün strategiyalar təklif edir",
            "əhəmiyyəti": [
                "Gözlənilməz hadisələrə hazırlıq",
                "Maliyyə itkilərinin minimizasiyası",
                "Uzunmüddətli davamlılıq",
                "İnvestor və kredit verən etibarı"
            ],
            "növləri": "Bazar riski, Operational risk, Maliyyə riski, Strateji risk"
        },
        "ümumi_risk_xalı": {
            "xal": round(risk_score, 2),
            "maksimum": 100,
            "səviyyə": "Yüksək Risk" if risk_score > 60 else "Orta Risk" if risk_score > 30 else "Aşağı Risk",
            "rəng_kodu": "Qırmızı" if risk_score > 60 else "Sarı" if risk_score > 30 else "Yaşıl"
        },
        "müəyyən_edilmiş_risklər": risks,
        "risk_metrikalari": {
            "volatillik": {
                "dəyər": round(volatility, 2),
                "vahid": "%",
                "qiymət": "Yüksək" if volatility > 20 else "Orta" if volatility > 10 else "Aşağı"
            },
            "aşağı_trend_volatilliyi": {
                "dəyər": round(downside_vol, 2),
                "vahid": "%",
                "izah": "Ortalamadan aşağı dəyərlərin dəyişkənliyi"
            },
            "VaR_95": {
                "dəyər": round(var_95, 2),
                "itki_potensiali": round(var_loss, 2),
                "izah": "95% ehtimalla ən pis ssenari bu dəyərdən yaxşı olacaq"
            },
            "konsentrasiya": {
                "maksimum_rüb": max(quarterly_dist, key=quarterly_dist.get),
                "faiz": round(max_quarter_conc, 2),
                "risk": "Yüksək" if max_quarter_conc > 30 else "Orta" if max_quarter_conc > 25 else "Aşağı"
            }
        },
        "risk_idarəetməsi_strategiyası": {
            "qısa_müddət": [
                "Cari riskləri yenidən qiymətləndirin",
                "Kritik metrikaları gündəlik izləyin",
                "Sürətli cavab planı hazırlayın"
            ],
            "orta_müddət": [
                "Diversifikasiya strategiyası hazırlayın",
                "Risk hedcinq mexanizmləri qur un",
                "Ehtiyat fondunu artırın"
            ],
            "uzun_müddət": [
                "Davamlı inkişaf modeli qurun",
                "Bazar asılılığını azaldın",
                "İnnovasiyaya investisiya edin"
            ]
        },
        "tövsiyə_olunan_tədbirlər": [
            {
                "prioritet": "Yüksək",
                "tədbir": r["azaldılması"][0] if "azaldılması" in r else "Risk idarəetməsi planı hazırlayın",
                "risk": r["kateqoriya"]
            }
            for r in risks[:3]  # Top 3 risks
        ] if risks else [
            {
                "prioritet": "Orta",
                "tədbir": "Risk monitorinq sistemini qur un",
                "risk": "Ümumi"
            }
        ]
    }


@router.get("/comparative-analysis", response_model=Dict[str, Any])
async def get_comparative_analysis():
    """
    🔄 Müqayisəli Təhlil

    Müxtəlif dövrlərin, rüblərin və illərin müqayisəsi
    """
    df = data_loader.df
    y = df['Nağd_pul_kredit_satışı'].values
    years = df['Year'].values
    quarters = df['Quarter'].values

    # Year-over-Year comparison
    yoy_comparison = []
    unique_years = sorted(df['Year'].unique())

    for i in range(1, len(unique_years)):
        prev_year = unique_years[i-1]
        curr_year = unique_years[i]

        prev_data = y[years == prev_year]
        curr_data = y[years == curr_year]

        prev_total = np.sum(prev_data)
        curr_total = np.sum(curr_data)

        growth = ((curr_total - prev_total) / prev_total * 100) if prev_total != 0 else 0

        yoy_comparison.append({
            "dövr": f"{prev_year} → {curr_year}",
            "əvvəlki_il": round(prev_total, 2),
            "cari_il": round(curr_total, 2),
            "dəyişiklik": round(curr_total - prev_total, 2),
            "artım_faizi": round(growth, 2),
            "qiymət": "Əla" if growth > 10 else "Yaxşı" if growth > 5 else "Zəif" if growth < 0 else "Orta"
        })

    # Quarter-over-Quarter comparison
    qoq_comparison = []
    for i in range(1, min(8, len(y))):  # Son 8 rüb
        prev_val = y[-(i+1)]
        curr_val = y[-i]
        growth = ((curr_val - prev_val) / prev_val * 100) if prev_val != 0 else 0

        qoq_comparison.append({
            "dövr": f"{df['Rüblər'].iloc[-(i+1)]} → {df['Rüblər'].iloc[-i]}",
            "əvvəlki_rüb": round(prev_val, 2),
            "cari_rüb": round(curr_val, 2),
            "dəyişiklik": round(curr_val - prev_val, 2),
            "artım_faizi": round(growth, 2)
        })

    # Quarterly seasonal comparison
    quarterly_comparison = {}
    for q in range(1, 5):
        q_data = y[quarters == q]
        if len(q_data) > 0:
            quarterly_comparison[f"Q{q}"] = {
                "ortalama": round(np.mean(q_data), 2),
                "median": round(np.median(q_data), 2),
                "minimum": round(np.min(q_data), 2),
                "maksimum": round(np.max(q_data), 2),
                "müşahidə_sayı": len(q_data),
                "ümumi_paya_töhfə": round(np.sum(q_data) / np.sum(y) * 100, 2),
                "son_dəyər": round(q_data[-1], 2) if len(q_data) > 0 else None
            }

    # Best and worst periods
    best_quarter_idx = np.argmax(y)
    worst_quarter_idx = np.argmin(y)

    # Trend comparison (first half vs second half)
    half_point = len(y) // 2
    first_half_avg = np.mean(y[:half_point])
    second_half_avg = np.mean(y[half_point:])
    overall_trend = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg != 0 else 0

    return {
        "müqayisəli_təhlil_nədir": {
            "təsvir": "Müqayisəli təhlil müxtəlif dövrlərin performansını yan-yana qoyaraq nümunələri və dəyişiklikləri görməyə kömək edir",
            "faydaları": [
                "Trend və mövsümiliyi aşkar etmək",
                "Ən yaxşı və ən pis dövrləri müəyyənləşdirmək",
                "Artım sürətini qiymətləndirmək",
                "Strateji qərarlar üçün əsas"
            ],
            "istifadə_sahələri": "Performans qiymətləndirmə, Büdcə planlaşdırma, Hədəf müəyyənləşdirmə"
        },
        "il_il_müqayisə": {
            "məlumat": yoy_comparison,
            "ortalama_artım": round(np.mean([x["artım_faizi"] for x in yoy_comparison]), 2) if yoy_comparison else 0,
            "ən_yaxşı_il": max(yoy_comparison, key=lambda x: x["artım_faizi"])["dövr"] if yoy_comparison else "N/A",
            "ən_zəif_il": min(yoy_comparison, key=lambda x: x["artım_faizi"])["dövr"] if yoy_comparison else "N/A"
        },
        "rüb_rüb_müqayisə": {
            "son_8_rüb": qoq_comparison,
            "ortalama_artım": round(np.mean([x["artım_faizi"] for x in qoq_comparison]), 2),
            "pozitiv_artım_sayı": len([x for x in qoq_comparison if x["artım_faizi"] > 0]),
            "neqativ_artım_sayı": len([x for x in qoq_comparison if x["artım_faizi"] < 0])
        },
        "rüblər_arası_müqayisə": quarterly_comparison,
        "ən_yaxşı_və_ən_pis": {
            "ən_yaxşı_rüb": {
                "dövr": df['Rüblər'].iloc[best_quarter_idx],
                "dəyər": round(y[best_quarter_idx], 2),
                "il": int(years[best_quarter_idx]),
                "rüb": int(quarters[best_quarter_idx])
            },
            "ən_pis_rüb": {
                "dövr": df['Rüblər'].iloc[worst_quarter_idx],
                "dəyər": round(y[worst_quarter_idx], 2),
                "il": int(years[worst_quarter_idx]),
                "rüb": int(quarters[worst_quarter_idx])
            },
            "fərq": round(y[best_quarter_idx] - y[worst_quarter_idx], 2),
            "faiz_fərq": round((y[best_quarter_idx] - y[worst_quarter_idx]) / y[worst_quarter_idx] * 100, 2) if y[worst_quarter_idx] != 0 else 0
        },
        "ümumi_trend": {
            "birinci_yarı_ortalama": round(first_half_avg, 2),
            "ikinci_yarı_ortalama": round(second_half_avg, 2),
            "ümumi_artım": round(overall_trend, 2),
            "istiqamət": "Yüksələn" if overall_trend > 0 else "Enən",
            "qiymət": "Güclü artım" if overall_trend > 20 else "Orta artım" if overall_trend > 0 else "Azalma"
        },
        "praktik_nəticələr": {
            "ən_güclü_rüb": max(quarterly_comparison, key=lambda q: quarterly_comparison[q]["ortalama"]),
            "ən_zəif_rüb": min(quarterly_comparison, key=lambda q: quarterly_comparison[q]["ortalama"]),
            "tövsiyə": [
                f"Ən güclü rüblərdə ({max(quarterly_comparison, key=lambda q: quarterly_comparison[q]['ortalama'])}) həcmi daha da artırmaq üçün resursları artırın",
                f"Ən zəif rüblərdə ({min(quarterly_comparison, key=lambda q: quarterly_comparison[q]['ortalama'])}) performansı yaxşılaşdırmaq üçün xüsusi kampaniyalar keçirin",
                "Ardıcıl artım üçün hər rübdə realistik hədəflər qoyun"
            ]
        }
    }


@router.get("/action-plan", response_model=Dict[str, Any])
async def get_action_plan():
    """
    📝 Fəaliyyət Planı

    Məlumat əsasında konkret addımlar və tövsiyələr
    """
    df = data_loader.df
    y = df['Nağd_pul_kredit_satışı'].values

    # Current situation analysis
    current_value = y[-1]
    trend = np.polyfit(range(8), y[-8:], 1)[0]
    volatility = np.std(y[-8:]) / np.mean(y[-8:]) * 100

    # Generate action items based on analysis
    actions = []

    # Priority 1: Address immediate issues
    if trend < 0:
        actions.append({
            "prioritet": 1,
            "kateqoriya": "Strateji",
            "başlıq": "Azalan Trendin Durdurulması",
            "təsvir": "Son 8 rübdə azalan trend müşahidə olunur. Təcili müdaxilə tələb olunur",
            "addımlar": [
                "Müştəri itkisi təhlili aparın (churn analysis)",
                "Rəqiblərin strategiyalarını araşdırın",
                "Müştəri məmnuniyyəti sorğusu keçirin",
                "Qiymət strategiyasını yenidən nəzərdən keçirin"
            ],
            "cavabdehlər": ["Marketinq İdarəsi", "Satış Departamenti", "Məhsul Meneceri"],
            "müddət": "1 ay",
            "gözlənilən_nəticə": "Trendin sabitləşməsi və ya müsbətə dönməsi"
        })
    else:
        actions.append({
            "prioritet": 1,
            "kateqoriya": "İnkişaf",
            "başlıq": "Artım Tempi nin Davam Etdirilməsi",
            "təsvir": "Müsbət trend davam edir. Bu momentumdən maksimum istifadə edin",
            "addımlar": [
                "Uğurlu satış strategiyalarını genişləndirin",
                "Yeni bazar seqmentlərinə gir in",
                "Brendinq və marketinq investisiyalarını artırın",
                "Müştəri bazasını genişləndirin"
            ],
            "cavabdehlər": ["Satış Direktoru", "Marketinq İdarəsi", "İnkişaf Departamenti"],
            "müddət": "3 ay",
            "gözlənilən_nəticə": "Artım tempinin saxlanması və ya artırılması"
        })

    # Priority 2: Risk management
    if volatility > 20:
        actions.append({
            "prioritet": 2,
            "kateqoriya": "Risk İdarəetməsi",
            "başlıq": "Volatilliyin Azaldılması",
            "təsvir": f"Yüksək dəyişkənlik ({volatility:.1f}%) planlaşdırmanı çətinləşdirir",
            "addımlar": [
                "Gəlir mənbələrini diversifikasiya edin",
                "Uzunmüddətli müqavilələr bağlayın",
                "Mövsümiliyə az asılı məhsullar əlavə edin",
                "Cash flow idarəetməsini təkmilləşdirin"
            ],
            "cavabdehlər": ["Maliyyə İdarəsi", "Risk Meneceri", "Məhsul İdarəsi"],
            "müddət": "6 ay",
            "gözlənilən_nəticə": "Volatilliyin 15%-dən aşağı salınması"
        })

    # Priority 3: Data and analytics
    actions.append({
        "prioritet": 3,
        "kateqoriya": "Analitika",
        "başlıq": "Proqnozlaşdırma Qabiliyyətinin Artırılması",
        "təsvir": "Daha dəqiq proqnozlar üçün analitik infrastrukturu gücləndirin",
        "addımlar": [
            "Əlavə məlumat mənbələri inteqrasiya edin (makroiqtisadi, müştəri davranışı)",
            "ML model lərini mütəmadi yeniləyin",
            "Real-time dashboard qurun",
            "Prediktiv analitika komandası yaradın"
        ],
        "cavabdehlər": ["Data Analitika", "IT İdarəsi", "İdarəetmə Komandası"],
        "müddət": "3 ay",
        "gözlənilən_nəticə": "Proqnoz xətasının 30-40% azalması"
    })

    # Priority 4: Quarterly optimization
    quarterly_avg = {q: np.mean(y[df['Quarter'] == q]) for q in range(1, 5)}
    weakest_quarter = min(quarterly_avg, key=quarterly_avg.get)

    actions.append({
        "prioritet": 4,
        "kateqoriya": "Mövsümilik",
        "başlıq": f"Q{weakest_quarter} Performansının Yaxşılaşdırılması",
        "təsvir": f"Q{weakest_quarter} ən zəif rübdür. Xüsusi tədbirlər tələb olunur",
        "addımlar": [
            f"Q{weakest_quarter} üçün xüsusi marketinq kampaniyası",
            "Bu rübdə xüsusi endirimlər və təşviqlər",
            "Satış komandası üçün Q{weakest_quarter} bonusları",
            "Müştəri engagement proqramları"
        ],
        "cavabdehlər": ["Marketinq", "Satış", "Məhsul İdarəsi"],
        "müddət": f"{weakest_quarter} aylar əvvəl planlaşdırma başlasın",
        "gözlənilən_nəticə": f"Q{weakest_quarter} performansında 20% artım"
    })

    # Priority 5: Long-term strategic
    actions.append({
        "prioritet": 5,
        "kateqoriya": "Strateji İnkişaf",
        "başlıq": "Davamlı Artım Strategiyası",
        "təsvir": "Uzunmüddətli rəqabət üstünlüyü üçün investisiyalar",
        "addımlar": [
            "Yeni məhsul xətləri araşdırın",
            "Texnoloji innovasiyaya investisiya edin",
            "Müştəri təcrübəsini təkmilləşdirin",
            "Bazar liderliyi strategiyası hazırlayın"
        ],
        "cavabdehlər": ["C-Suite", "Strateji Planlaşdırma", "İnnovasiya İdarəsi"],
        "müddət": "12 ay",
        "gözlənilən_nəticə": "Bazar payında 5-10% artım"
    })

    # Implementation timeline
    timeline = {
        "1_ay": [a["başlıq"] for a in actions if "1 ay" in a["müddət"]],
        "3_ay": [a["başlıq"] for a in actions if "3 ay" in a["müddət"]],
        "6_ay": [a["başlıq"] for a in actions if "6 ay" in a["müddət"]],
        "12_ay": [a["başlıq"] for a in actions if "12 ay" in a["müddət"]]
    }

    return {
        "fəaliyyət_planı_nədir": {
            "təsvir": "Fəaliyyət planı məlumat təhlilindən əldə edilmiş nəticələri konkret addımlara çevirir",
            "prinsiplər": [
                "SMART (Specific, Measurable, Achievable, Relevant, Time-bound)",
                "Prioritetlərə əsaslanır",
                "Cavabdehlər müəyyənləşdirilir",
                "Nəticələr ölçülə biləndir"
            ],
            "əhəmiyyəti": "Təhlilsiz fəaliyyət kor addımlardır, fəaliyyətsiz təhlil isə boş sözdür"
        },
        "cari_vəziyyət": {
            "son_dəyər": round(current_value, 2),
            "trend": "Artım" if trend > 0 else "Azalma",
            "trend_sürəti": round(trend, 2),
            "volatillik": round(volatility, 2),
            "ümumi_status": "Yaxşı" if trend > 0 and volatility < 15 else "Diqqət Tələb Edir" if trend < 0 else "Orta"
        },
        "fəaliyyətlər": actions,
        "icra_qrafiki": timeline,
        "uğur_göstəriciləri": {
            "qısa_müddət": [
                "Növbəti rübdə trend dəyişikliyi",
                "Müştəri məmnuniyyət xalı",
                "Satış konversiya faizi"
            ],
            "orta_müddət": [
                "6 aylıq ortalama artım faizi",
                "Volatillik əmsalı",
                "Hədəflərə çatma faizi"
            ],
            "uzun_müddət": [
                "İllik artım faizi",
                "Bazar payı",
                "Müştəri retention faizi",
                "ROI (Return on Investment)"
            ]
        },
        "izləmə_və_qiymətləndirmə": {
            "tezlik": {
                "həftəlik": "Əsas metrikaların izlənməsi (satış, lead, conversion)",
                "aylıq": "Performans icmalı və fəaliyyət planı proqres yoxlanışı",
                "rüblük": "KPI qiymətləndirməsi və strategiya yenilənməsi",
                "illik": "Strateji planlama və hədəf müəyyənləşdirmə"
            },
            "metodologiya": [
                "Key metrikalar dashboard-da real-time izlənilir",
                "Hər fəaliyyət üçün owner progress hesabatı verir",
                "Aylıq steering committee görüşləri",
                "Data-driven qərar qəbuletmə mədəniyyəti"
            ]
        },
        "növbəti_addımlar": [
            "Bu planı əsas maraqdar tərəflərlə paylaşın",
            "Hər fəaliyyət üçün detal iqra planı hazırlayın",
            "Resurs və büdcə ayrın",
            "Kickoff görüşü təşkil edin",
            "İzləmə sistemini qur un və işə salın"
        ]
    }
