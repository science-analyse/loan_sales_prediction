"""
Kredit Satışı Analitika API
FastAPI Backend with Analytics Routes in Azerbaijani
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
from pathlib import Path

# Import routes
from app.routes import analytics, statistics, predictions, insights, dashboard_analytics

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

# Include routers - THESE MUST BE FIRST
app.include_router(dashboard_analytics.router, prefix="/api/analytics", tags=["📊 Dashboard Analytics"])
app.include_router(dashboard_analytics.router, prefix="/api/predictions", tags=["🔮 Predictions"])  # Simple forecast for dashboard
app.include_router(analytics.router, prefix="/api/az/analytics", tags=["📊 Analitika (AZ)"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["📈 Statistika"])
app.include_router(predictions.router, prefix="/api/az/predictions", tags=["🔮 Proqnozlar (AZ)"])  # AZ endpoints
app.include_router(insights.router, prefix="/api/insights", tags=["💡 Təhlillər"])

# Health check
@app.get("/health")
async def health_check():
    """Sağlamlıq yoxlaması"""
    return {
        "status": "sağlam",
        "tarix": datetime.now().isoformat(),
        "xidmət": "işləyir"
    }

# Determine frontend directory path
static_dir = Path(__file__).parent.parent / "frontend" / "dist"
if not static_dir.exists():
    # Try alternative path for development
    static_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"

# Mount static files and setup SPA routing
if static_dir.exists() and (static_dir / "index.html").exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    # Serve static files (vite.svg, etc)
    @app.get("/vite.svg")
    async def serve_vite_svg():
        return FileResponse(static_dir / "vite.svg")

    # Root route - serve frontend
    @app.get("/")
    async def serve_frontend():
        """Serve frontend application"""
        return FileResponse(static_dir / "index.html")

    # SPA catch-all - MUST BE LAST
    # This handles client-side routing
    @app.api_route("/{path_name:path}", methods=["GET"])
    async def serve_spa(request: Request, path_name: str):
        """Serve SPA for all other GET requests"""
        # Let API routes, docs, etc pass through
        if path_name.startswith(("api/", "docs", "redoc", "openapi.json", "health", "assets/")):
            raise HTTPException(status_code=404, detail="Not found")
        # Serve index.html for all other routes (client-side routing)
        return FileResponse(static_dir / "index.html")
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

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port="8000",
        reload=True,
        log_level="info"
    )
