# Travel Planner API

A FastAPI-based API for planning travel itineraries and getting travel suggestions using AI.

## Features

- Generate detailed travel plans with day-by-day itineraries
- Get specific travel suggestions and information about destinations
- Powered by Grok-2 AI model via LangChain
- Redis caching for improved performance

## Setup

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your configuration (see `.env.example`):
   ```
   XAI_API_KEY=your_api_key_here
   ENV=development
   REDIS_HOST=localhost
   REDIS_PORT=6379
   CACHE_TTL=3600
   ```
5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

### Docker Deployment

1. Clone the repository
2. Create a `.env` file with your configuration (see `.env.example`)
3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```
4. Access the API at http://localhost:8000

## API Endpoints

### Generate Travel Plan

```
POST /api/v1/plan
```

Request body:
```json
{
  "destination": "Tokyo, Japan",
  "duration": 3,
  "interests": "food and culture",
  "start_date": "2023-12-01"  // Optional
}
```

### Get Travel Suggestions

```
POST /api/v1/suggest
```

Request body:
```json
{
  "destination": "Tokyo, Japan",
  "query": "What are the best times to visit Mt. Fuji?"
}
```

## Documentation

API documentation is available at `/docs` when the server is running.

## Development

In development mode, the `/api/v1/plan` endpoint returns a mock response for faster testing.

## Caching

The API uses Redis for caching responses to improve performance and reduce API calls to the AI service. The cache TTL (time-to-live) can be configured in the `.env` file. 

## Migration

# Local development
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head

# In Docker
docker-compose exec api alembic revision --autogenerate -m "Description of changes"
docker-compose exec api alembic upgrade head

