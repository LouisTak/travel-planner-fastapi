from fastapi import FastAPI
from functools import lru_cache
import config
from controllers.ai_controller import router as ai_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Travel Planner API",
    description="API for planning travel itineraries and getting travel suggestions using AI",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@lru_cache()
def get_settings():
    return config.settings()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Travel Planner API"}

# Include the AI router
app.include_router(ai_router, prefix="/api/v1")