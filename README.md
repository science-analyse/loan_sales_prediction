# 💰 Kredit Satışı Analitika / Loan Sales Analytics

Full-stack analitika və proqnozlaşdırma tətbiqi. Nağd pul kredit satışı məlumatları üçün ətraflı analitika, trend təhlili və gələcək proqnozlar.

## 🎯 Xüsusiyyətlər

### 📊 Dashboard
- **Əsas Göstəricilər**: Son dövr, ortalama, minimum, maksimum
- **Trend Təhlili**: İstiqamət, güclülük (R²), rüblük dəyişmə
- **Risk Qiymətləndirməsi**: Avtomatik risk səviyyəsi müəyyənləşdirmə
- **İnteraktiv Qrafiklər**: Real-time məlumat vizuallaşdırması

### 🔮 Proqnoz
- **Kombinə Proqnoz Modeli**: Moving Average, Weighted MA, Exponential Smoothing
- **Etibar İntervalları**: 95% etibar sərhədləri
- **Vizual Proqnozlar**: Area chart ilə trend göstərimi
- **Rüblük Proqnozlar**: Q1, Q2, Q3, Q4 üçün ayrıca proqnozlar

### 💡 Təhlillər
- **İcraçı Xülasəsi**: Əsas rəqəmlər və dəyişikliklər
- **Risk Təhlili**: Dərinlikli risk qiymətləndirməsi
- **Biznes Tövsiyələri**: Actionable insights
- **Prioritetli Məsələlər**: Diqqət tələb edən sahələr

### 📅 Rüblük Təhlil
- **Rüblər Üzrə Müqayisə**: Q1-Q4 statistikası
- **Ən Yaxşı/Ən Zəif Rüblər**: Performance rankings
- **Səbəb Təhlili**: Niyə yaxşı/zəif olduğunu izah edir
- **Strategiya Tövsiyələri**: Hər rüb üçün xüsusi tövsiyələr

## 🛠️ Texnologiyalar

### Backend
- **FastAPI**: Yüksək performanslı Python web framework
- **Pandas & NumPy**: Data analizi
- **SciPy & Statsmodels**: Statistik analiz
- **Scikit-learn**: Machine learning modellər

### Frontend
- **React 18**: Modern UI library
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Data visualization
- **Axios**: HTTP client

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Single-container deployment**: Cost-effective unified deployment

## 🚀 Quraşdırma

### Development Mode

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs

### Production Deployment (Single Container)

```bash
# Build və deploy et
docker-compose up --build -d

# Tətbiqi aç
open http://localhost:8000
```

Daha ətraflı məlumat üçün bax: [DEPLOY.md](./DEPLOY.md)

## 📁 Struktur

```
loan_sales_prediction/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Ana tətbiq (static files serveri daxil)
│   │   ├── routes/          # API route-ları
│   │   │   ├── analytics.py
│   │   │   ├── statistics.py
│   │   │   ├── predictions.py
│   │   │   └── insights.py
│   │   └── utils/
│   │       └── data_loader.py
│   └── requirements.txt
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── App.jsx          # Ana komponent
│   │   ├── services/
│   │   │   └── api.js       # API inteqrasiyası
│   │   └── index.css
│   ├── dist/                # Production build (git ignored)
│   ├── package.json
│   └── tailwind.config.js
├── notebooks/               # Data analizi
│   └── data/
│       └── ml_ready_data.csv
├── Dockerfile.unified       # Unified Docker build
├── docker-compose.yml       # Docker compose konfiqurasiyası
├── DEPLOY.md               # Deployment guide
└── README.md               # Bu fayl
```

## 🔌 API Endpoints

### Analytics
- `GET /api/analytics/dashboard` - Əsas dashboard məlumatları
- `GET /api/analytics/detailed-statistics` - Ətraflı statistika
- `GET /api/analytics/outlier-analysis` - Outlier təhlili
- `GET /api/analytics/trend-analysis` - Trend təhlili
- `GET /api/analytics/quarterly-insights` - Rüblük insights

### Statistics
- `GET /api/statistics/descriptive` - Təsviri statistika
- `GET /api/statistics/correlation` - Korrelyasiya analizi
- `GET /api/statistics/normality-tests` - Normallik testləri

### Predictions
- `GET /api/predictions/simple-forecast?periods=4` - Sadə proqnoz
- `GET /api/predictions/seasonal-forecast?periods=4` - Seasonal proqnoz
- `GET /api/predictions/confidence-levels` - Etibar səviyyələri
- `GET /api/predictions/model-comparison` - Model müqayisəsi

### Insights
- `GET /api/insights/executive-summary` - İcraçı xülasəsi
- `GET /api/insights/performance-metrics` - Performance metrikləri
- `GET /api/insights/risk-analysis` - Risk təhlili
- `GET /api/insights/comparative-analysis` - Müqayisəli təhlil
- `GET /api/insights/action-plan` - Fəaliyyət planı

## 🎨 Design Features

### Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Horizontal scroll for tabs on mobile
- Hidden columns on small screens

### Modern UI
- Gradient backgrounds
- Hover effects and animations
- Smooth transitions
- Card-based layout
- Color-coded insights (green/yellow/red)

### Accessibility
- Clear contrast ratios
- Readable font sizes
- Icon support
- Loading states
- Error handling

## 📊 Data Requirements

### Input Data Format
CSV faylı aşağıdakı sütunlara malik olmalıdır:
- **DATE**: Tarix (YYYY-MM-DD)
- **Sum_cashLoan**: Kredit məbləği (manat)

Minimum 12 ay məlumat tələb olunur.

## 🔒 Təhlükəsizlik

- CORS konfiqurasiyası
- Environment variables
- Docker isolation
- Health checks
- Error handling
- Input validation

## 📈 Performance

- **Singleton DataLoader**: Data yalnız bir dəfə yüklənir
- **Multi-stage Docker build**: Kiçik image ölçüsü
- **Frontend caching**: Static assets cache
- **Uvicorn workers**: Paralel request handling
- **Gzip compression**: Reduced transfer size

## 💰 Cost Optimization

✅ Single container deployment
✅ No separate database required
✅ Minimal resource usage
✅ Free tier compatible on most platforms

## 📝 License

Proprietary - Internal Use Only

## 👥 Contributors

- Data Science Team
- Backend Development Team
- Frontend Development Team

## 📞 Support

Problemlə qarşılaşsanız:
1. Logları yoxlayın: `docker-compose logs -f app`
2. Health check: `curl http://localhost:8000/health`
3. API docs: http://localhost:8000/docs

---

Made with ❤️ for data-driven decision making
