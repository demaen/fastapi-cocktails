from fastapi.security.api_key import APIKeyHeader
from fastapi import FastAPI, HTTPException, Security, Depends
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from typing import List, Dict
from models.cocktail import CocktailRecipe  # Import your existing model

load_dotenv()  # Load environment variables from .env file

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(title="Cocktail Recipes API")

# Path to data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Welcome to Cocktail Recipes API"}

@app.get("/cocktails/", response_model=List[str])
async def list_cocktails():
    """Get a list of all available cocktails"""
    try:
        return [f.stem for f in DATA_DIR.glob("*.json")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cocktails/{name}")
async def get_cocktail(name: str):
    """Get a specific cocktail recipe by name"""
    try:
        file_path = DATA_DIR / f"{name}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Cocktail {name} not found")
        
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cocktails/ingredient/{ingredient}")
async def get_cocktail_by_ingredient(ingredient: str):
    """Get cocktails by ingredient"""
    try:
        cocktails = []
        search_term = ingredient.lower()
        
        for file_path in DATA_DIR.glob("*.json"):
            with open(file_path, "r") as f:
                cocktail = json.load(f)
                # Extract ingredient names, handling both string and dictionary cases
                ingredient_names = []
                for i in cocktail["ingredients"]:
                    if isinstance(i, dict):
                        # If ingredient is a dictionary, try to get the name/ingredient field
                        ingredient_names.append(i.get("name", "") or i.get("ingredient", ""))
                    elif isinstance(i, str):
                        ingredient_names.append(i)
                
                # Check if search term is contained within any ingredient name
                if any(search_term in ing.lower() for ing in ingredient_names if ing):
                    cocktails.append(cocktail["name"])
                    
        if not cocktails:
            raise HTTPException(status_code=404, detail=f"No cocktails found with ingredient {ingredient}")
        return cocktails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cocktails/glass/{glass}")
async def get_cocktail_by_glass(glass: str):
    """Get cocktails by glass type"""
    try:
        cocktails = []
        search_term = glass.lower()

        for file_path in DATA_DIR.glob("*.json"):
            with open(file_path, "r") as f:
                cocktail = json.load(f)
                # Check if search term is contained within the glass field
                if search_term in cocktail["glass"].lower():
                    cocktails.append(cocktail["name"])

        if not cocktails:
            raise HTTPException(status_code=404, detail=f"No cocktails found with glass {glass}")
        return cocktails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header is None:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="API Key missing")
    if api_key_header != os.getenv("API_KEY"):  # Store your API key in environment variables
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return api_key_header
    
# add a new cocktail including inredients, glasstype, instructions category
@app.post("/cocktails/")
async def add_cocktail(cocktail: CocktailRecipe, api_key: str = Depends(get_api_key)):
    """Add a new cocktail"""
    try:
        name = cocktail.name
        file_path = DATA_DIR / f"{name}.json"
        if file_path.exists():
            raise HTTPException(status_code=409, detail=f"Cocktail {name} already exists")

        with open(file_path, "w") as f:
            json.dump(cocktail.model_dump(), f, indent=4)

        return {"message": f"Cocktail {name} added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
