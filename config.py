"""
Configuration module for YouTube Recipe Generator
Contains all constants, tags, and configuration settings
"""

import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
CONFIG_FILE = BASE_DIR / ".env"

# Ensure directories exist
ASSETS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Default placeholder image
PLACEHOLDER_IMAGE_URL = "https://example.com/placeholder.jpg"

# Gemini API Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"
GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json"
}

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

# Mealee App Constants
VALID_UNITS = [
    "ml", "l", "linguriță", "lingură", "cană",
    "g", "kg",
    "buc", "bucată", "fire", "cățel", "frunze", "legătură",
    "plic", "conservă", "la gust", "după preferință"
]

VALID_DIFFICULTIES = ["beginner", "intermediate", "advanced"]
VALID_CATEGORIES = ["breakfast", "lunch", "dinner", "snack", "dessert"]
VALID_CUISINES = ["romanian", "italian", "asian", "mexican", "mediterranean", "american"]

# Complete list of available tags (from Mealee app)
AVAILABLE_TAGS = [
    # Dietary preferences
    "vegetarian", "vegan", "lacto-vegetarian", "ovo-vegetarian",

    # Allergen-free
    "fără gluten", "fără lactate", "fără nuci", "fără soia", "fără ou",

    # Nutritional goals
    "low-carb", "high-protein", "low-fat", "high-fiber",
    "low-calorie", "moderate-calorie", "high-calorie",

    # Health & wellness
    "sănătos", "detox", "energizant", "imunitate", "antiinflamator",
    "pentru diabetici", "pentru gravide",

    # Time-based
    "rapid", "moderat", "îndelungat",

    # Skill level
    "începător", "intermediar", "avansat",

    # Cooking method
    "fără gătit", "la cuptor", "la grătar", "la aragaz",
    "slow cooker", "instant pot", "air fryer",

    # Cost & accessibility
    "economic", "ingrediente simple", "premium", "sezonier",

    # Meal type
    "mic dejun", "prânz", "cină", "gustare", "desert",

    # Occasion
    "festiv", "party", "picnic", "sărbători", "romantic",
    "pentru copii", "pentru bebeluși",

    # Cultural & regional
    "tradițional", "regional", "mediteranean", "asian",
    "italian", "mexican", "american", "românesc",

    # Special diets
    "keto", "paleo", "whole30", "raw", "DASH",

    # Texture & presentation
    "crocant", "cremos", "proaspăt", "instagramabil",

    # Special properties
    "batch cooking", "congelabil", "rămășițe", "un singur vas", "fără ulei",

    # Additional
    "pentru familie", "single serving", "prăjit", "fierbințel", "rece"
]

# GUI Text (Romanian)
GUI_TEXT = {
    "window_title": "Generator Rețete YouTube",
    "api_key_label": "Cheia API Gemini:",
    "api_key_save": "Salvează",
    "tags_label": "Etichete Disponibile (separate prin virgulă):",
    "urls_label": "Link-uri YouTube (unul pe linie):",
    "urls_placeholder": "Introduceți link-uri YouTube aici...\nExemplu: https://www.youtube.com/watch?v=...",
    "generate_button": "Generează Rețete",
    "progress_label": "Progres:",
    "preview_button": "Previzualizare",
    "export_button": "Exportă JSON",
    "confirmation_title": "Confirmare Rețetă",
    "confirmation_warning": "⚠ Acest video nu are transcriere.\nGemini a generat rețeta bazat pe conținutul vizual.",
    "confirmation_accept": "Da",
    "confirmation_edit": "Editare",
    "confirmation_reject": "Nu",
    "success_message": "✓ Generat {count} rețete cu succes!",
    "export_success": "✓ Rețete exportate în: {path}",
    "error_no_api_key": "Vă rugăm să introduceți cheia API Gemini.",
    "error_no_urls": "Vă rugăm să introduceți cel puțin un link YouTube.",
    "error_invalid_url": "✗ URL invalid: {url}",
    "error_processing": "✗ Eroare la procesare: {error}"
}

def load_api_key():
    """Load API key from .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv(CONFIG_FILE)
        return os.getenv("GEMINI_API_KEY", "")
    except ImportError:
        # If python-dotenv is not installed, try to read file directly
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        return line.split("=", 1)[1].strip()
        return ""

def save_api_key(api_key: str):
    """Save API key to .env file"""
    with open(CONFIG_FILE, "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
