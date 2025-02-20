from pydantic import BaseModel
from typing import List

class Ingredient(BaseModel):
    name: str
    amount: float
    unit: str

class CocktailRecipe(BaseModel):
    name: str
    ingredients: List[Ingredient]
    instructions: List[str]
    glass_type: str
    category: str = "Uncategorized"