"""
Kredit Satışı Analitika API
FastAPI Backend with Analytics Routes in Azerbaijani
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

# Import routes
from app.routes import analytics, statistics, predictions, insights

# Create FastAPI app
app = FastAPI(
    title="Kredit Satışı Analitika API",
    description="Nağd pul kredit satışı üçün ətraflı analitika və proqnozlaşdırma API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production-da bunu məhdudlaşdırın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["📊 Analitika"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["📈 Statistika"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["🔮 Proqnozlar"])
app.include_router(insights.router, prefix="/api/insights", tags=["💡 Təhlillər"])

@app.get("/")
async def root():
    """Ana səhifə - API haqqında məlumat"""
    return {
        "mesaj": "Kredit Satışı Analitika API-yə xoş gəlmisiniz!",
        "versiya": "1.0.0",
        "tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sənədlər": {
            "Swagger UI": "/docs",
            "ReDoc": "/redoc"
        },
        "mövcud_endpoint-lər": {
            "analitika": "/api/analytics",
            "statistika": "/api/statistics",
            "proqnozlar": "/api/predictions",
            "təhlillər": "/api/insights"
        },
        "təsvir": "Bu API kredit satışı məlumatları üçün ətraflı analitika, statistik təhlillər və proqnozlaşdırma imkanları təqdim edir."
    }

@app.get("/health")
async def health_check():
    """Sağlamlıq yoxlaması"""
    return {
        "status": "sağlam",
        "tarix": datetime.now().isoformat(),
        "xidmət": "işləyir"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
