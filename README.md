# Cocktail Recipes API

A FastAPI-based REST API for managing cocktail recipes stored in JSON files.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload
```

## API Endpoints

```markdown
- `GET /`: Welcome message
- `GET /cocktails/`: List all available cocktails
- `GET /cocktails/{name}`: Get a specific cocktail recipe
- `GET /cocktails/ingredient/{ingredient}`: Find cocktails containing a specific ingredient
- `GET /cocktails/glass/{glass}`: Find cocktails using a specific glass type
- `POST /cocktails/`: Add a new cocktail recipe
- `GET /docs`: Interactive API documentation (Swagger UI)

```

## Data Structure

Cocktail recipes are stored as JSON files in the `data` directory. Each recipe includes:
- Name
- List of ingredients (with amounts and units)
- Instructions
- Glass type
- Category