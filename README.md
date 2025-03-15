# Travel Planner API

A FastAPI-based API for planning travel itineraries and getting travel suggestions using AI.

## Features

- Generate detailed travel plans with day-by-day itineraries
- Get specific travel suggestions and information about destinations
- Powered by Grok-2 AI model via LangGraph
- Redis caching for improved performance
- Robust error handling and retry logic

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

## LangGraph Implementation

The API uses LangGraph to implement a robust workflow for generating travel plans and suggestions. The workflow includes:

- Automatic retry logic for handling errors
- Validation of generated plans
- Conditional branching based on the state of the workflow
- Fallback mechanisms for handling failures

## Testing

To run the tests:

```bash
# Run all tests
TESTING=1 python -m pytest

# Run specific tests
TESTING=1 python tests/test_ai_graph.py
```

The `TESTING=1` environment variable ensures that the tests use mock data instead of making actual API calls.


## Migration

# Local development
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head

# In Docker
docker-compose exec api alembic revision --autogenerate -m "Description of changes"
docker-compose exec api alembic upgrade head

# Install new packages
docker-compose exec api pip install -r requirements.txt
