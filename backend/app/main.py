"""
Kredit Satışı Analitika API
FastAPI Backend with Analytics Routes in Azerbaijani
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
from pathlib import Path

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

# Serve static frontend files
static_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    @app.get("/")
    async def serve_frontend():
        """Serve frontend application"""
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Frontend not built yet. Run 'npm run build' in frontend directory."}

    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        """Catch all routes for SPA"""
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404, detail="Not found")
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Frontend not found")
else:
    @app.get("/")
    async def root():
        """Ana səhifə - API haqqında məlumat"""
        return {
            "mesaj": "Kredit Satışı Analitika API-yə xoş gəlmisiniz!",
            "versiya": "1.0.0",
            "tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "qeyd": "Frontend qurulmayıb. Frontend qovluğunda 'npm run build' əmrini işə salın.",
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
