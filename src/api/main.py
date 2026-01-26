from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import properties, investment_scores, insights

app = FastAPI(
    title="STR Investment Analysis API",
    description="API for analyzing short-term rental investment opportunities",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(properties.router)
app.include_router(investment_scores.router)
app.include_router(insights.router)

@app.get("/")
def root():
    return {
        "message": "STR Investment Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "properties": "/properties",
            "analysis": "/properties/{id}/analysis",
            "insights": "/insights/top-performers"
        }
    }