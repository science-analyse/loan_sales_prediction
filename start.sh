#!/bin/bash

# Loan Sales Analytics - Quick Start Script
# Bu skript tətbiqi sürətli başlatmaq üçündür

echo "🚀 Kredit Satışı Analitika - Quick Start"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker quraşdırılmayıb. Xahiş edirik Docker quraşdırın."
    echo "   https://www.docker.com/get-started"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose quraşdırılmayıb. Xahiş edirik Docker Compose quraşdırın."
    exit 1
fi

echo "✅ Docker və Docker Compose tapıldı"
echo ""

# Check if data file exists
if [ ! -f "notebooks/data/ml_ready_data.csv" ]; then
    echo "⚠️  Data faylı tapılmadı: notebooks/data/ml_ready_data.csv"
    echo "   Xahiş edirik ml_ready_data.csv faylını notebooks/data/ qovluğuna əlavə edin"
    exit 1
fi

echo "✅ Data faylı tapıldı"
echo ""

# Build and start the application
echo "🔨 Tətbiqi qururam və başlatıram..."
echo ""

docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tətbiq uğurla başladı!"
    echo ""
    echo "📱 Tətbiqi açın:"
    echo "   Frontend: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Health Check: http://localhost:8000/health"
    echo ""
    echo "📋 Faydalı əmrlər:"
    echo "   Logları görmək: docker-compose logs -f app"
    echo "   Dayandırmaq: docker-compose down"
    echo "   Yenidən başlatmaq: docker-compose restart"
    echo ""
    echo "⏳ Tətbiq başlayana qədər 10-15 saniyə gözləyin..."
    echo ""

    # Wait for application to be ready
    echo "🔍 Tətbiqi yoxlayıram..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Tətbiq hazırdır!"
            echo ""
            echo "🎉 Tətbiq uğurla işə düşdü!"
            echo "   Brauzerinizdə açın: http://localhost:8000"
            exit 0
        fi
        echo -n "."
        sleep 1
    done

    echo ""
    echo "⚠️  Tətbiq hələ cavab vermir. Logları yoxlayın:"
    echo "   docker-compose logs -f app"
else
    echo ""
    echo "❌ Xəta baş verdi. Logları yoxlayın:"
    echo "   docker-compose logs app"
    exit 1
fi
