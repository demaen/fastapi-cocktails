import json
from pathlib import Path
from typing import Dict

class CocktailManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    def _read_json_file(self, file_path: Path) -> Dict:
        """Helper method to read JSON file"""
        with open(file_path, "r") as f:
            return json.load(f)

    def _write_json_file(self, file_path: Path, data: Dict) -> None:
        """Helper method to write JSON file"""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def _has_ingredient(self, cocktail: Dict, search_term: str) -> bool:
        """Helper method to check if cocktail has ingredient"""
        for ingredient in cocktail["ingredients"]:
            if isinstance(ingredient, dict):
                ingredient_name = ingredient.get("name", "") or ingredient.get("ingredient", "")
            else:
                ingredient_name = ingredient
            if search_term in ingredient_name.lower():
                return True
        return False
