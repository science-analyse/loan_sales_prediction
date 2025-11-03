
# SARIMAX Produksiya Modeli İstifadə Təlimatı

## Model Məlumatı
- Versiya: 1.0.0
- Yaradılma tarixi: 20251102_234406
- Model tipi: SARIMAX(0, 0, 0)(0, 1, 0, 4)

## Model Yükləmə

```python
import pickle

# Modeli yüklə
with open('models/sarimax_production_v1.0.0_20251102_234406.pkl', 'rb') as f:
    model = pickle.load(f)

# Proqnoz
future_forecast = model.forecast(steps=4)  # Növbəti 4 rüb
print(future_forecast)
```

## Performans
- Test R²: -0.0144
- Test MAE: 25,139.95 manat
- Cross-validation MAE: 19,699.14 manat

## Tövsiyələr
1. Hər rüb yeni məlumatlarla modeli yenidən qur
2. Proqnozları faktiki dəyərlərlə müqayisə edərək model performansını izlə
3. Əgər MAE >20% artarsa, modeli yenidən qur
4. Mövsümi nümunələrdə dəyişiklik olduqda parametrləri yenidən optimallaşdır

## Əlaqə
Model haqqında suallar üçün data science komandasına müraciət edin.
