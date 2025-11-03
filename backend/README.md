# Kredit Satışı Analitika API - Deployment Guide

Nağd pul kredit satışı üçün ətraflı analitika və proqnozlaşdırma API.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop)

### Deployment Options

#### Option 1: Using Docker Compose (Recommended)

From the project root directory:

```bash
# Build and start the service
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Stop the service
docker-compose down
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Option 2: Using Docker directly

```bash
cd backend

# Build the image
docker build -t loan-analytics-api .

# Run the container
docker run -d \
  --name loan-analytics \
  -p 8000:8000 \
  -v $(pwd)/../notebooks/data:/app/notebooks/data:ro \
  loan-analytics-api

# Check logs
docker logs -f loan-analytics

# Stop and remove container
docker stop loan-analytics
docker rm loan-analytics
```

#### Option 3: Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 API Endpoints

### Analytics (`/api/analytics`)
- `GET /dashboard` - Main dashboard with key metrics
- `GET /detailed-statistics` - Comprehensive statistical analysis
- `GET /outlier-analysis` - Outlier detection (IQR & Z-score)
- `GET /trend-analysis` - Trend analysis with linear regression
- `GET /quarterly-insights` - Seasonal analysis and recommendations

### Statistics (`/api/statistics`)
- `GET /descriptive` - Descriptive statistics
- `GET /correlation` - Correlation matrix
- `GET /normality-tests` - Normality tests (Shapiro-Wilk, etc.)
- `GET /hypothesis-testing` - Hypothesis tests (t-tests, ANOVA, etc.)

### Predictions (`/api/predictions`)
- `GET /simple-forecast?periods=4` - Simple forecasting methods
- `GET /seasonal-forecast?periods=4` - Seasonal forecasting
- `GET /confidence-levels` - Forecast accuracy metrics
- `GET /model-comparison` - Compare forecasting models

### Insights (`/api/insights`)
- `GET /executive-summary` - Executive overview
- `GET /performance-metrics` - KPI metrics
- `GET /risk-analysis` - Risk assessment
- `GET /comparative-analysis` - Period comparisons
- `GET /action-plan` - Data-driven action items

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# API Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=2

# CORS (adjust for production)
ALLOWED_ORIGINS=*

# Environment
ENVIRONMENT=production
```

### Production Deployment

For production, update `docker-compose.yml`:

1. **Remove development volumes**:
   ```yaml
   # Comment out this line in docker-compose.yml
   # - ./backend/app:/app/app:ro
   ```

2. **Add Nginx reverse proxy** (optional):
   - Uncomment nginx service in docker-compose.yml
   - Configure SSL certificates
   - Update CORS origins

3. **Resource limits**:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
           reservations:
             cpus: '1'
             memory: 512M
   ```

4. **Logging**:
   ```yaml
   services:
     backend:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "sağlam",
  "tarix": "2025-11-03T08:46:50.950428",
  "xidmət": "işləyir"
}
```

### Test API Endpoints
```bash
# Dashboard
curl http://localhost:8000/api/analytics/dashboard | jq

# Forecast next 4 quarters
curl "http://localhost:8000/api/predictions/simple-forecast?periods=4" | jq

# Executive summary
curl http://localhost:8000/api/insights/executive-summary | jq
```

## 🛠️ Troubleshooting

### Check container status
```bash
docker-compose ps
docker-compose logs backend
```

### Rebuild after code changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Access container shell
```bash
docker-compose exec backend /bin/bash
```

### Check data file access
```bash
docker-compose exec backend ls -la /app/notebooks/data/
```

## 📝 Docker Commands Cheat Sheet

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild services
docker-compose build

# Scale service (multiple instances)
docker-compose up -d --scale backend=3

# Check resource usage
docker stats

# Remove unused images
docker system prune -a
```

## 🔒 Security Considerations

For production deployment:

1. **Update CORS origins** in `app/main.py`:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. **Use environment variables** for sensitive data

3. **Enable HTTPS** with nginx reverse proxy

4. **Set resource limits** in docker-compose.yml

5. **Regular updates**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## 📦 Data Requirements

Ensure the data file exists:
```
notebooks/data/ml_ready_data.csv
```

The file should contain:
- `Rüblər` - Quarter labels (e.g., "2024 Q1")
- `Year` - Year values
- `Quarter` - Quarter numbers (1-4)
- `Nağd_pul_kredit_satışı` - Target variable

## 🌐 Cloud Deployment

### Deploy to AWS (ECS/EC2)
```bash
# Build for specific platform
docker build --platform linux/amd64 -t loan-analytics-api .

# Tag for ECR
docker tag loan-analytics-api:latest YOUR_ECR_REPO:latest

# Push to ECR
docker push YOUR_ECR_REPO:latest
```

### Deploy to Azure Container Instances
```bash
az container create \
  --resource-group myResourceGroup \
  --name loan-analytics \
  --image loan-analytics-api \
  --dns-name-label loan-analytics \
  --ports 8000
```

### Deploy to Google Cloud Run
```bash
gcloud run deploy loan-analytics \
  --image loan-analytics-api \
  --platform managed \
  --port 8000 \
  --allow-unauthenticated
```

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs -f backend`
- Verify data file location
- Ensure Docker has sufficient resources (CPU, RAM)
- Check port 8000 is not already in use

## 📄 License

[Your License Here]
