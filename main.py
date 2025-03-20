from fastapi import FastAPI
from functools import lru_cache
import config
from controllers.ai_controller import router as ai_router
from controllers.authentication_controller import router as auth_router
from controllers.travel_plan_controller import router as travel_plan_router
from controllers.user_controller import router as user_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
app = FastAPI(
    title="Travel Planner API",
    description="API for planning travel itineraries and getting travel suggestions using AI",
    version="1.0.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
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
    return config.settings  # Return the settings instance, not calling it as a function

@app.get("/")
def read_root():
    return {"message": "Welcome to the Travel Planner API"}

# Include the AI router
app.include_router(ai_router, prefix="/api/v1")

# Include the authentication router
app.include_router(auth_router, prefix="/api/v1")

# Include the travel plan router
app.include_router(travel_plan_router, prefix="/api/v1")

# Include the user router
app.include_router(user_router, prefix="/api/v1")