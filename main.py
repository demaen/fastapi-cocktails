from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.responses import HTMLResponse
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv
import os
from typing import List, Dict
from models.cocktail import CocktailRecipe
from services.cocktail_manager import CocktailManager
from fuzzywuzzy import fuzz

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Cocktail Recipes API",
    description="An API for managing cocktail recipes",
    version="0.1.1",
    openapi_version="3.0.2",
    openapi_tags=[{"name": "cocktails", "description": "Operations with cocktails"}]
)

# Initialize the cocktail manager
cocktail_manager = CocktailManager()

async def verify_api_key(api_key_header: str = Security(APIKeyHeader(name="X-API-Key"))):
    """Verify API key middleware"""
    if api_key_header is None:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="API Key missing")
    if api_key_header != os.getenv("API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return api_key_header

@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    """Serve emoji favicon"""
    return HTMLResponse(
        '''
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🍸</text></svg>">
        '''
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Cocktail Recipes API"}

@app.get("/cocktails/", response_model=List[str], tags=["cocktails"])
async def list_cocktails():
    """Get a list of all available cocktails"""
    try:
        return [f.stem for f in cocktail_manager.data_dir.glob("*.json")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cocktails: {str(e)}")

@app.get("/cocktails/{name}", tags=["cocktails"])
async def get_cocktail(name: str) -> Dict:
    """Get a specific cocktail recipe by name"""
    # Normalize the search term
    normalized_name = name.lower().strip()
    
    # Search through all cocktail files
    for file_path in cocktail_manager.data_dir.glob("*.json"):
        try:
            cocktail_data = cocktail_manager._read_json_file(file_path)
            # Case-insensitive comparison
            if cocktail_data["name"].lower().strip() == normalized_name:
                return cocktail_data
                
            # # Optional: Add fuzzy matching for similar names
            # if fuzz.ratio(cocktail_data["name"].lower(), normalized_name) > 85:
            #     return cocktail_data
                
        except Exception as e:
            continue  # Skip files that can't be read
            
    raise HTTPException(
        status_code=404, 
        detail=f"Cocktail '{name}' not found"
    )

@app.get("/cocktails/ingredient/{ingredient}", tags=["cocktails"])
async def get_cocktail_by_ingredient(ingredient: str) -> List[str]:
    """Get cocktails by ingredient"""
    search_term = ingredient.lower()
    cocktails = []
    
    try:
        for file_path in cocktail_manager.data_dir.glob("*.json"):
            cocktail = cocktail_manager._read_json_file(file_path)
            if cocktail_manager._has_ingredient(cocktail, search_term):
                cocktails.append(cocktail["name"])
                
        if not cocktails:
            raise HTTPException(status_code=404, 
                              detail=f"No cocktails found with ingredient {ingredient}")
        return cocktails
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, 
                          detail=f"Error searching by ingredient: {str(e)}")
    
@app.get("/cocktails/ingredients/{ingredients}", tags=["cocktails"])
async def get_cocktail_by_ingredients(ingredients: str) -> List[str]:
    """Get cocktails by multiple ingredients
    
    Parameters:
        ingredients (str): Comma-separated list of ingredient names to search for
        
    Returns:
        List[str]: List of cocktail names that contain all the specified ingredients
        
    Raises:
        HTTPException: 404 if no cocktails found with ingredients
                      500 if error occurs during search
    """
    search_terms = [ingredient.lower().strip() for ingredient in ingredients.split(",")]
    cocktails = []

    try:
        for file_path in cocktail_manager.data_dir.glob("*.json"):
            cocktail = cocktail_manager._read_json_file(file_path)
            if all(cocktail_manager._has_ingredient(cocktail, term) for term in search_terms):
                cocktails.append(cocktail["name"])

        if not cocktails:
            raise HTTPException(status_code=404,
                              detail=f"No cocktails found with ingredients {ingredients}")
        return cocktails
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,
                          detail=f"Error searching by ingredients: {str(e)}") 

@app.get("/cocktails/glass/{glass}", tags=["cocktails"])
async def get_cocktail_by_glass(glass: str) -> List[str]:
    """Get cocktails by glass type"""
    search_term = glass.lower()
    cocktails = []
    
    try:
        for file_path in cocktail_manager.data_dir.glob("*.json"):
            cocktail = cocktail_manager._read_json_file(file_path)
            if search_term in cocktail["glass_type"].lower():
                cocktails.append(cocktail["name"])

        if not cocktails:
            raise HTTPException(status_code=404, 
                              detail=f"No cocktails found with glass {glass}")
        return cocktails
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, 
                          detail=f"Error searching by glass: {str(e)}")
    
@app.get("/cocktails/ingredients/", tags=["cocktails"]) 
async def get_list_of_ingredients() -> List[str]:
    """Get a list of all available ingredients"""
    ingredients = set()
    try:
        for file_path in cocktail_manager.data_dir.glob("*.json"):
            cocktail = cocktail_manager._read_json_file(file_path)
            for ingredient in cocktail["ingredients"]:
                ingredients.add(ingredient["name"])
        return sorted(list(ingredients))
    except Exception as e:
        raise HTTPException(status_code=500,
                          detail=f"Error listing ingredients: {str(e)}")
    
@app.get("/cocktails/glasses/", tags=["cocktails"])
async def get_list_of_glasses() -> List[str]:
    """Get a list of all available glasses"""
    glasses = set()
    try:
        for file_path in cocktail_manager.data_dir.glob("*.json"):
            cocktail = cocktail_manager._read_json_file(file_path)
            glasses.add(cocktail["glass_type"])
        return sorted(list(glasses))
    except Exception as e:
        raise HTTPException(status_code=500,
                          detail=f"Error listing glasses: {str(e)}")

@app.post("/cocktails/", tags=["cocktails"])
async def add_cocktail(cocktail: CocktailRecipe, 
                      api_key: str = Depends(verify_api_key)) -> Dict:
    """Add a new cocktail"""
    file_path = cocktail_manager.data_dir / f"{cocktail.name}.json"
    if file_path.exists():
        raise HTTPException(status_code=409, 
                          detail=f"Cocktail {cocktail.name} already exists")

    try:
        cocktail_manager._write_json_file(file_path, cocktail.model_dump())
        return {"message": f"Cocktail {cocktail.name} added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, 
                          detail=f"Error adding cocktail: {str(e)}")
