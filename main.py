from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.responses import HTMLResponse
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv
import os
from typing import List, Dict
from models.cocktail import CocktailRecipe
from services.cocktail_manager import CocktailManager

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

@app.get("/cocktails/", response_model=List[str])
async def list_cocktails():
    """Get a list of all available cocktails"""
    try:
        return [f.stem for f in cocktail_manager.data_dir.glob("*.json")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cocktails: {str(e)}")

@app.get("/cocktails/{name}")
async def get_cocktail(name: str) -> Dict:
    """Get a specific cocktail recipe by name"""
    file_path = cocktail_manager.data_dir / f"{name}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Cocktail {name} not found")
    
    try:
        return cocktail_manager._read_json_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading cocktail: {str(e)}")

@app.get("/cocktails/ingredient/{ingredient}")
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

@app.get("/cocktails/glass/{glass}")
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

@app.post("/cocktails/")
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
