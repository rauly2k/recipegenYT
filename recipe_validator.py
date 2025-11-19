"""
Recipe Validator Module
Validates recipe JSON against schema and business rules
"""

import jsonschema
from typing import Tuple

# Recipe JSON Schema
RECIPE_SCHEMA = {
    "type": "object",
    "required": [
        "recipeId", "title", "description", "imageUrl",
        "prepTime", "cookTime", "totalTime", "servings",
        "difficulty", "ingredients", "instructions",
        "nutrition", "tags", "category", "cuisine",
        "createdBy", "createdAt"
    ],
    "properties": {
        "recipeId": {"type": "string", "minLength": 10},
        "title": {"type": "string", "minLength": 5, "maxLength": 100},
        "description": {"type": "string", "minLength": 20, "maxLength": 500},
        "imageUrl": {"type": "string"},
        "prepTime": {"type": "integer", "minimum": 1, "maximum": 480},
        "cookTime": {"type": "integer", "minimum": 0, "maximum": 720},
        "totalTime": {"type": "integer", "minimum": 1, "maximum": 1200},
        "servings": {"type": "integer", "minimum": 1, "maximum": 20},
        "difficulty": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
        "ingredients": {
            "type": "array",
            "minItems": 1,
            "maxItems": 50,
            "items": {
                "type": "object",
                "required": ["name", "quantity", "unit"],
                "properties": {
                    "name": {"type": "string", "minLength": 2},
                    "quantity": {"type": "number", "minimum": 0},
                    "unit": {
                        "type": "string",
                        "enum": [
                            "ml", "l", "linguriță", "lingură", "cană",
                            "g", "kg",
                            "buc", "bucată", "fire", "cățel", "frunze", "legătură",
                            "plic", "conservă", "la gust", "după preferință"
                        ]
                    }
                }
            }
        },
        "instructions": {
            "type": "array",
            "minItems": 1,
            "maxItems": 30,
            "items": {"type": "string", "minLength": 10}
        },
        "nutrition": {
            "type": "object",
            "required": ["calories", "protein", "carbs", "fats"],
            "properties": {
                "calories": {"type": "number", "minimum": 0},
                "protein": {"type": "number", "minimum": 0},
                "carbs": {"type": "number", "minimum": 0},
                "fats": {"type": "number", "minimum": 0},
                "healthScore": {"type": "integer", "minimum": 0, "maximum": 100}
            }
        },
        "tags": {
            "type": "array",
            "minItems": 3,
            "maxItems": 7,
            "items": {"type": "string"}
        },
        "category": {
            "type": "string",
            "enum": ["breakfast", "lunch", "dinner", "snack", "dessert"]
        },
        "cuisine": {
            "type": "string",
            "enum": ["romanian", "italian", "asian", "mexican", "mediterranean", "american"]
        },
        "createdBy": {"type": "string"},
        "createdAt": {"type": "string"},
        "isFavorite": {"type": "boolean"}
    }
}

def validate_recipe(recipe_json: dict, available_tags: list) -> Tuple[bool, str]:
    """
    Validates recipe JSON against schema and business rules

    Args:
        recipe_json: Recipe dictionary to validate
        available_tags: List of allowed tags

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # Schema validation
    try:
        jsonschema.validate(instance=recipe_json, schema=RECIPE_SCHEMA)
    except jsonschema.ValidationError as e:
        return False, f"Schema validation error: {e.message}"

    # Tag validation
    recipe_tags = recipe_json.get('tags', [])
    invalid_tags = [tag for tag in recipe_tags if tag not in available_tags]
    if invalid_tags:
        return False, f"Invalid tags: {', '.join(invalid_tags)}"

    # Time validation
    prep_time = recipe_json.get('prepTime', 0)
    cook_time = recipe_json.get('cookTime', 0)
    total_time = recipe_json.get('totalTime', 0)

    if total_time < (prep_time + cook_time):
        return False, f"totalTime ({total_time}) must be >= prepTime ({prep_time}) + cookTime ({cook_time})"

    # Required tag categories (relaxed - not strictly enforced)
    meal_tags = {'mic dejun', 'prânz', 'cină', 'gustare', 'desert'}
    difficulty_tags = {'începător', 'intermediar', 'avansat'}
    time_tags = {'rapid', 'moderat', 'îndelungat'}

    # Check if at least one tag from each category is present (warning only)
    warnings = []

    if not any(tag in meal_tags for tag in recipe_tags):
        warnings.append("No meal type tag found")

    if not any(tag in difficulty_tags for tag in recipe_tags):
        warnings.append("No difficulty tag found")

    if not any(tag in time_tags for tag in recipe_tags):
        warnings.append("No time duration tag found")

    # Return success (warnings are informational only)
    if warnings:
        return True, f"Valid with warnings: {'; '.join(warnings)}"

    return True, "Valid"

def validate_batch(recipes: list, available_tags: list) -> Tuple[list, list]:
    """
    Validate multiple recipes

    Args:
        recipes: List of recipe dictionaries
        available_tags: List of allowed tags

    Returns:
        Tuple of (valid_recipes, errors)
        - valid_recipes: List of valid recipe dictionaries
        - errors: List of error messages for invalid recipes
    """
    valid_recipes = []
    errors = []

    for i, recipe in enumerate(recipes):
        is_valid, message = validate_recipe(recipe, available_tags)

        if is_valid:
            valid_recipes.append(recipe)
            if "warnings" in message.lower():
                errors.append(f"Recipe {i+1} ({recipe.get('title', 'Unknown')}): {message}")
        else:
            errors.append(f"Recipe {i+1} ({recipe.get('title', 'Unknown')}): {message}")

    return valid_recipes, errors
