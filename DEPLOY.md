# 🚀 Deployment Guide / Quraşdırma Təlimatı

## Single-Container Deployment (Frontend + Backend Together)

This application deploys both frontend and backend in a single Docker container for cost-effective deployment.

### Prerequisites / Tələblər
- Docker və Docker Compose quraşdırılmalıdır
- Minimum 1GB RAM
- Minimum 2GB disk space

### Quick Start / Sürətli Başlanğıc

#### 1. Layihəni Klonlayın
```bash
git clone <repository-url>
cd loan_sales_prediction
```

#### 2. Data Faylını Əlavə Edin
```bash
# ml_ready_data.csv faylını notebooks/data/ qovluğuna əlavə edin
cp /path/to/ml_ready_data.csv notebooks/data/
```

#### 3. Docker Container-i Qurun və İşə Salın
```bash
# Build and start the container
docker-compose up --build -d

# Logları izləyin
docker-compose logs -f app
```

#### 4. Tətbiqi Açın
Brauzerinizdə açın: **http://localhost:8000**

- Frontend: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Container İdarəetməsi

```bash
# Container-i dayandırın
docker-compose down

# Container-i yenidən başladın
docker-compose restart

# Logları görün
docker-compose logs -f app

# Container-ə daxil olun
docker-compose exec app bash
```

### Production Deployment / İstehsalat Quraşdırması

#### Cloud Platforms

**1. Render.com** (Recommended for easy deployment)
```bash
# Render.com-da yeni Web Service yaradın
# - Build Command: docker-compose build
# - Start Command: docker-compose up
# - Port: 8000
```

**2. Railway.app**
```bash
# Railway CLI ilə
railway up
```

**3. DigitalOcean App Platform**
```bash
# Docker Compose faylını yükləyin
# Auto-deploy konfiqurasiya ediləcək
```

**4. AWS ECS / EC2**
```bash
# EC2 instance-də
sudo yum install docker
sudo service docker start
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose up -d
```

### Problemlərin Həlli / Troubleshooting

#### Container başlamır
```bash
# Logları yoxlayın
docker-compose logs app

# Container-i yenidən qurun
docker-compose down
docker-compose up --build
```

#### Data faylı tapılmır
```bash
# Data faylının olduğunu yoxlayın
ls -la notebooks/data/ml_ready_data.csv

# Əgər yoxdursa, əlavə edin
cp /path/to/ml_ready_data.csv notebooks/data/
docker-compose restart
```

#### Port artıq istifadədədir
```bash
# docker-compose.yml-də portu dəyişdirin
# ports:
#   - "8080:8000"  # 8080-ə dəyişdirin

docker-compose up -d
```

### Performans Optimallaşdırması

#### 1. Worker Sayını Artırın
`Dockerfile.unified`-də dəyişdirin:
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 2. Resource Limitləri
`docker-compose.yml`-ə əlavə edin:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### Təhlükəsizlik / Security

#### 1. CORS-u Məhdudlaşdırın
`backend/app/main.py`-də:
```python
allow_origins=["https://yourdomain.com"]
```

#### 2. Environment Variables
`.env` faylı yaradın:
```env
ENVIRONMENT=production
SECRET_KEY=your-secret-key
```

### Backup və Restore

#### Backup
```bash
# Data faylını backup edin
docker-compose exec app cp /app/notebooks/data/ml_ready_data.csv /backup/
```

#### Restore
```bash
# Data faylını restore edin
docker-compose exec app cp /backup/ml_ready_data.csv /app/notebooks/data/
```

### Monitoring

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Container Stats
```bash
docker stats loan-analytics-app
```

### Cost Optimization / Xərc Optimallaşdırması

✅ **Single container** - Yalnız bir container, aşağı xərc
✅ **No separate database** - CSV fayldan oxuyur
✅ **Efficient caching** - DataLoader singleton pattern
✅ **Small image size** - Multi-stage build istifadə edir

Təxmini Aylıq Xərclər:
- **Render.com Free Tier**: $0 (750 saat/ay pulsuz)
- **Railway Free Tier**: $0 ($5 kredit)
- **DigitalOcean Droplet**: $6/ay (1GB RAM)
- **AWS Lightsail**: $5/ay

### Support

Problemlə qarşılaşsanız:
1. Logları yoxlayın: `docker-compose logs -f app`
2. Container statusunu yoxlayın: `docker-compose ps`
3. Health check edin: `curl http://localhost:8000/health`
