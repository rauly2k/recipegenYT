"""
Gemini Service Module
Handles communication with Google Gemini API for recipe extraction
"""

import json
from datetime import datetime
from typing import Dict
import google.generativeai as genai

from config import (
    GEMINI_MODEL,
    GENERATION_CONFIG,
    SAFETY_SETTINGS,
    PLACEHOLDER_IMAGE_URL
)

# Comprehensive Recipe Extraction Prompt
RECIPE_EXTRACTION_PROMPT = """
Tu ești un expert în extragerea și structurarea rețetelor culinare din videoclipuri YouTube.

# MISIUNE
Analizează videoclipul YouTube de la link-ul furnizat și extrage o rețetă de gătit structurată în format JSON, gata pentru import direct într-o aplicație de management rețete.

# LINK VIDEO
{youtube_url}

# INSTRUCȚIUNI CRITICE

## 1. LIMBA
- TOT conținutul generat (titlu, descriere, ingrediente, instrucțiuni) TREBUIE să fie în limba ROMÂNĂ
- Cheile JSON rămân în engleză (ex: "title", "ingredients", "instructions")
- Nu traduce unitățile de măsură - folosește unitățile românești standard

## 2. STRUCTURĂ JSON OBLIGATORIE

Generează un JSON cu EXACT această structură:

```json
{{
  "recipeId": "generat_automat_uuid_v4",
  "title": "Titlul rețetei în română",
  "description": "Descriere scurtă a rețetei (1-2 propoziții, română)",
  "imageUrl": "https://example.com/placeholder.jpg",
  "prepTime": 15,
  "cookTime": 30,
  "totalTime": 45,
  "servings": 4,
  "difficulty": "beginner",
  "ingredients": [
    {{
      "name": "nume ingredient în română (lowercase)",
      "quantity": 250.0,
      "unit": "g"
    }}
  ],
  "instructions": [
    "Pasul 1 detaliat în limba română",
    "Pasul 2 detaliat în limba română"
  ],
  "nutrition": {{
    "calories": 350.0,
    "protein": 25.0,
    "carbs": 40.0,
    "fats": 12.0,
    "healthScore": 65
  }},
  "tags": [
    "rapid",
    "sănătos",
    "low-carb"
  ],
  "category": "dinner",
  "cuisine": "romanian",
  "createdBy": "youtube_import",
  "createdAt": "2025-11-19T10:30:00Z",
  "isFavorite": false,
  "no_transcript_warning": false
}}
```

## 3. CÂMPURI OBLIGATORII - SPECIFICAȚII DETALIATE

### recipeId
- Generează un UUID v4 unic
- Format: "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"

### title
- Limba: ROMÂNĂ
- Lungime: 10-100 caractere
- Specific și descriptiv (ex: "Ciorbă de perișoare cu smântână și mărar")
- Fără emojis

### description
- Limba: ROMÂNĂ
- Lungime: 50-200 caractere
- Rezumat apetisant al rețetei
- Menționează ingredientele principale sau caracteristica unică

### imageUrl
- Folosește ÎNTOTDEAUNA: "https://example.com/placeholder.jpg"
- NU căuta sau generezi URL-uri de imagini reale

### prepTime (minute)
- Tip: întreg (integer)
- Interval: 1-480 minute
- Doar timpul de pregătire ÎNAINTE de gătit (spălat, tăiat, amestecat)

### cookTime (minute)
- Tip: întreg (integer)
- Interval: 1-720 minute
- Doar timpul de gătit propriu-zis (la cuptor, la aragaz, etc.)
- Pentru rețete "fără gătit": pune 0

### totalTime (minute)
- Tip: întreg (integer)
- Formula: prepTime + cookTime
- Adaugă timp de odihnă dacă este esențial (ex: dospirea aluatului)

### servings
- Tip: întreg (integer)
- Interval: 1-20
- Număr realist de porții

### difficulty
- Valori PERMISE: "beginner", "intermediate", "advanced"
- Bazează decizia pe:
  - beginner: <5 ingrediente principale, <30 min total, tehnici simple
  - intermediate: 5-15 ingrediente, 30-90 min, tehnici moderate
  - advanced: >15 ingrediente, >90 min, tehnici complexe

### ingredients
- Array de obiecte
- Minimum: 1 ingredient
- Maximum: 50 ingrediente

Pentru FIECARE ingredient:

**name** (string, română):
- Lowercase complet (ex: "piept de pui", NU "Piept De Pui")
- Specific (ex: "roșii cherry", nu doar "roșii")
- Fără cantități în nume (cantitatea este în "quantity")
- Folosește ingredientele standard românești

**quantity** (number):
- Tip: float/double
- Valoare numerică (ex: 250.0, 1.5, 0.5)
- NU pune text (ex: NU "2-3", folosește 2.5)

**unit** (string):
- OBLIGATORIU să folosești DOAR aceste unități:

**Volum**: ml, l, linguriță, lingură, cană
**Greutate**: g, kg
**Bucăți**: buc, bucată, fire, cățel, frunze, legătură
**Altele**: plic, conservă, la gust, după preferință

- Exemplu CORECT: {{"name": "făină", "quantity": 250, "unit": "g"}}
- Exemplu GREȘIT: {{"name": "făină", "quantity": 250, "unit": "grame"}}

### instructions
- Array de string-uri
- Minimum: 1 pas
- Maximum: 30 pași
- Limba: ROMÂNĂ
- Format: imperativ (ex: "Spălați...", "Tăiați...", "Amestecați...")
- Fiecare pas = o propoziție completă și clară
- Ordine logică: de la pregătire la servire
- Detalii concrete (temperaturi, timpi, tehnici)

Exemplu:
```json
[
  "Spălați și curățați carnea de pui, apoi tăiați-o în cuburi de aproximativ 2 cm.",
  "Încălziți uleiul într-o tigaie la foc mediu și prăjiți cuburile de carne până devin aurii (aproximativ 5-7 minute).",
  "Adăugați ceapa tocată și usturoiul și gătiți încă 2 minute până devin fragede.",
  "Turnați bulionul de pui, aduceți la fierbere, apoi reduceți focul și lăsați să fiarbă la foc mic 20 de minute.",
  "Serviți cald, garnisit cu pătrunjel proaspăt tocat."
]
```

### nutrition
- Toate valorile: per porție (NU pentru întreaga rețetă)
- Tip: float/double

**calories** (kcal per porție):
- Interval realist: 100-1200 kcal per porție
- Estimează bazat pe ingrediente
- Exemplu: salată = 150-300, paste = 400-600, desert = 300-500

**protein** (grame per porție):
- Interval: 5-60g
- Surse principale: carne, pește, ouă, lactate, leguminoase

**carbs** (grame per porție):
- Interval: 10-100g
- Surse: cereale, paste, orez, pâine, cartofi, zahăr

**fats** (grame per porție):
- Interval: 5-50g
- Surse: ulei, unt, smântână, nuci, carne grasă

**healthScore** (0-100):
- 80-100: foarte sănătos (salate, quinoa bowls, legume la grătar)
- 60-79: sănătos (paste integrale, pui la cuptor)
- 40-59: moderat (paste carbonara, pizza)
- 20-39: indulgent (burgeri, prăjeli)
- 0-19: foarte indulgent (deserturi bogate, fast-food)

### tags
- Array de string-uri
- Minimum: 3 taguri
- Maximum: 7 taguri
- OBLIGATORIU să folosești DOAR taguri din lista furnizată mai jos

**LISTA COMPLETĂ DE TAGURI DISPONIBILE:**
{available_tags}

**REGULI DE TAGARE:**

1. Alege 3-7 taguri RELEVANTE
2. Include OBLIGATORIU:
   - 1 tag de tip masă: mic dejun, prânz, cină, gustare, desert
   - 1 tag de dificultate: începător, intermediar, avansat
   - 1 tag de timp: rapid, moderat, îndelungat

3. Adaugă taguri suplimentare relevante:
   - Dietă: vegetarian, vegan, low-carb, high-protein, etc.
   - Alergeni: fără gluten, fără lactate, fără nuci, etc.
   - Stil: tradițional, festiv, pentru copii, etc.
   - Cost: economic, premium
   - Metodă: la cuptor, la grătar, fără gătit, etc.

**Exemplu pentru Papanași:**
```json
["desert", "tradițional", "intermediar", "moderat", "festiv", "prăjit"]
```

**Exemplu pentru Salată de quinoa:**
```json
["prânz", "sănătos", "vegan", "rapid", "începător", "fără gătit", "high-protein"]
```

### category
- Valori PERMISE: "breakfast", "lunch", "dinner", "snack", "dessert"
- Alege 1 singură categorie (cea mai potrivită)

Ghid:
- breakfast: omleta, clătite, cereale, toast
- lunch: supe, salate, paste, sandwiches
- dinner: friptură, tocană, paste, pizza
- snack: chips, popcorn, batoane, smoothie
- dessert: prăjituri, înghețată, mousse, fructe

### cuisine
- Valori PERMISE: "romanian", "italian", "asian", "mexican", "mediterranean", "american"

Ghid:
- romanian: sarmale, mici, ciorbă, mămăligă, papanași
- italian: pasta, pizza, risotto, tiramisu
- asian: stir-fry, sushi, curry, pho, pad thai
- mexican: tacos, burritos, quesadillas, guacamole
- mediterranean: hummus, falafel, greek salad, moussaka
- american: burgers, hot dogs, mac & cheese, brownies

### createdBy
- Folosește ÎNTOTDEAUNA: "youtube_import"

### createdAt
- Format: ISO 8601 (ex: "2025-11-19T10:30:00Z")
- Folosește timestamp-ul curent

### isFavorite
- Folosește ÎNTOTDEAUNA: false

### no_transcript_warning
- Setează la true DOAR dacă videoclipul nu are transcriere disponibilă
- Altfel: false

## 4. VALIDARE FINALĂ

Înainte de a returna JSON-ul, verifică:

✓ Toate câmpurile obligatorii sunt prezente
✓ Toate valorile sunt în română (exceptând cheile)
✓ Toate unitățile sunt din lista permisă
✓ Toate tagurile sunt din lista furnizată
✓ difficulty, category, cuisine au valori valide
✓ Nutrition values sunt realiste per porție
✓ prepTime + cookTime = totalTime
✓ ingredients au name, quantity, unit complete
✓ instructions au minim 3 pași clari

## 5. ANALIZĂ VIDEO

- Vizionează videoclipul complet (dacă posibil)
- Extrage informații din:
  - Titlul și descrierea video
  - Transcrierea (dacă disponibilă)
  - Conținutul vizual (ingrediente afișate, tehnici de gătit)
  - Audio (instrucțiuni verbale)
- Dacă lipsesc informații: estimează rezonabil bazat pe rețete similare

# OUTPUT FINAL

Returnează DOAR obiectul JSON, fără text suplimentar, fără markdown code blocks.
Asigură-te că JSON-ul este valid și poate fi parsat direct.
"""

def call_gemini_api(video_url: str, available_tags: list, api_key: str) -> Dict:
    """
    Calls Gemini API to extract recipe from YouTube video

    Args:
        video_url: YouTube video URL
        available_tags: List of allowed tags
        api_key: Google Gemini API key

    Returns:
        dict: Recipe JSON object

    Raises:
        Exception: If API call fails or response is invalid
    """
    # Configure Gemini
    genai.configure(api_key=api_key)

    # Create model instance
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config=GENERATION_CONFIG,
        safety_settings=SAFETY_SETTINGS
    )

    # Format available tags as comma-separated string
    tags_str = ", ".join(available_tags)

    # Build prompt
    prompt = RECIPE_EXTRACTION_PROMPT.format(
        youtube_url=video_url,
        available_tags=tags_str
    )

    try:
        # Send request
        response = model.generate_content(prompt)

        # Extract text from response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove ```

        response_text = response_text.strip()

        # Parse JSON response
        recipe_json = json.loads(response_text)

        # Add current timestamp if missing
        if not recipe_json.get('createdAt'):
            recipe_json['createdAt'] = datetime.utcnow().isoformat() + 'Z'

        # Ensure placeholder image URL is set
        if not recipe_json.get('imageUrl') or recipe_json['imageUrl'] == '':
            recipe_json['imageUrl'] = PLACEHOLDER_IMAGE_URL

        # Ensure isFavorite is set
        if 'isFavorite' not in recipe_json:
            recipe_json['isFavorite'] = False

        return recipe_json

    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response from Gemini: {str(e)}")
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

def sanitize_youtube_url(url: str) -> str:
    """
    Extract clean YouTube video URL

    Args:
        url: Raw YouTube URL

    Returns:
        str: Clean YouTube URL

    Raises:
        ValueError: If URL is not a valid YouTube URL
    """
    import re

    # Extract video ID
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"

    raise ValueError(f"Invalid YouTube URL: {url}")

def is_valid_youtube_url(url: str) -> bool:
    """
    Check if URL is a valid YouTube URL

    Args:
        url: URL to check

    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    try:
        sanitize_youtube_url(url)
        return True
    except ValueError:
        return False
