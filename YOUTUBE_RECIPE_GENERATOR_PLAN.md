# YouTube Recipe Generator - Implementation Plan

**Project:** Python Desktop Application for YouTube Recipe Extraction
**Target App:** Mealee (Flutter Recipe Management App)
**Date:** 2025-11-19
**Language:** Romanian (GUI + Content)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technical Architecture](#technical-architecture)
3. [GUI Design Specification](#gui-design-specification)
4. [Processing Pipeline](#processing-pipeline)
5. [Gemini API Integration](#gemini-api-integration)
6. [JSON Output Format](#json-output-format)
7. [Implementation Steps](#implementation-steps)
8. [Dependencies & Requirements](#dependencies--requirements)
9. [Error Handling & Edge Cases](#error-handling--edge-cases)
10. [Testing Checklist](#testing-checklist)

---

## 1. Project Overview

### Purpose
Extract cooking recipes from YouTube videos and convert them into structured JSON format for direct import into the Mealee app.

### Core Features
- ✅ Accept single or multiple YouTube video links
- ✅ Process videos using Google Gemini 2.5 Pro API (no transcript extraction needed)
- ✅ Generate structured recipes in Romanian with proper tags
- ✅ Export ready-to-import JSON file
- ✅ Preview recipes before export with user confirmation option
- ✅ Romanian GUI with progress tracking

### Key Requirements
- **Language:** GUI labels and all recipe content in Romanian
- **Input:** YouTube video URLs (one per line)
- **Output:** JSON file with English keys, Romanian values
- **Tags:** Must use predefined tags from Mealee app (100+ available)
- **No Manual Editing:** Recipes should be import-ready without modification

---

## 2. Technical Architecture

### Technology Stack
```
┌─────────────────────────────────────┐
│   GUI Layer (Tkinter)               │
│   - Romanian labels                 │
│   - Multi-line URL input            │
│   - API key management              │
│   - Progress display                │
│   - Recipe preview & confirmation   │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   Processing Layer (Python)         │
│   - YouTube link validation         │
│   - Gemini API communication        │
│   - Recipe structure validation     │
│   - JSON export                     │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│   External Services                 │
│   - Google Gemini 2.5 Pro API       │
│   - YouTube (video metadata)        │
└─────────────────────────────────────┘
```

### File Structure
```
youtube-recipe-generator/
│
├── main.py                      # GUI application entry point
├── gemini_service.py            # Gemini API interaction
├── recipe_validator.py          # JSON schema validation
├── config.py                    # App configuration & constants
├── assets/
│   └── placeholder.jpg          # Default recipe image
├── output/
│   └── recipes_export.json      # Generated recipe file
├── requirements.txt             # Python dependencies
└── README.md                    # Setup & usage instructions
```

---

## 3. GUI Design Specification

### Window Layout (Romanian Labels)

```
┌──────────────────────────────────────────────────────────────┐
│  Generator Rețete YouTube                                [×] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Cheia API Gemini:                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ AIzaSy...                                      [Salvează]│ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Etichete Disponibile (separate prin virgulă):             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ vegetarian,vegan,fără gluten,low-carb,rapid,desert...  │ │
│  │ (scroll area - pre-filled with all 100+ tags)          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Link-uri YouTube (unul pe linie):                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ https://www.youtube.com/watch?v=...                    │ │
│  │ https://www.youtube.com/watch?v=...                    │ │
│  │                                                          │ │
│  │                                                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│           ┌─────────────────────────────────┐               │
│           │    Generează Rețete             │               │
│           └─────────────────────────────────┘               │
│                                                              │
│  Progres:                                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Se procesează video 1/3: "Sarmale tradiționale"...     │ │
│  │ ✓ Video 1 finalizat                                    │ │
│  │ ⚠ Video 2: Fără transcriere - confirmare necesară      │ │
│  │                                                          │ │
│  │ (Auto-scroll to bottom)                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────┐  ┌──────────────────────────┐  │
│  │  Previzualizare        │  │  Exportă JSON            │  │
│  └────────────────────────┘  └──────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### GUI Components Breakdown

#### 1. API Key Input
```python
Label: "Cheia API Gemini:"
Field: Entry widget (password-like with show/hide toggle)
Button: "Salvează" (saves to config file)
Validation: Check if key starts with "AIzaSy"
```

#### 2. Tags Management Area
```python
Label: "Etichete Disponibile (separate prin virgulă):"
Field: ScrolledText widget (4 lines height)
Default Value: Pre-filled with all 100+ Mealee tags
Purpose: Allow users to customize tag list if needed
```

#### 3. YouTube URLs Input
```python
Label: "Link-uri YouTube (unul pe linie):"
Field: ScrolledText widget (10 lines height)
Validation: Check for youtube.com or youtu.be URLs
Placeholder: "Introduceți link-uri YouTube aici..."
```

#### 4. Generate Button
```python
Text: "Generează Rețete"
Action: Start processing pipeline
State: Disabled during processing
```

#### 5. Progress Log Area
```python
Label: "Progres:"
Field: ScrolledText widget (8 lines height, read-only)
Auto-scroll: Yes (to bottom)
Example Output:
  - "Se inițializează Gemini API..."
  - "Se procesează video 1/3: [video title]..."
  - "✓ Video 1 finalizat - Rețetă: Ciorbă de perișoare"
  - "⚠ Video 2: Fără transcriere - confirmare necesară"
  - "✓ Generat 3 rețete cu succes"
```

#### 6. Preview & Export Buttons
```python
Button 1: "Previzualizare" (shows generated recipes in popup)
Button 2: "Exportă JSON" (saves to file)
State: Enabled only after successful generation
```

### Confirmation Dialog (for videos without transcript)

When Gemini processes a video without transcript:

```
┌──────────────────────────────────────────────────────────────┐
│  Confirmare Rețetă                                      [×]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Video: https://www.youtube.com/watch?v=...                 │
│  Titlu: "Sarmale tradiționale moldovenești"                │
│                                                              │
│  ⚠ Acest video nu are transcriere.                         │
│  Gemini a generat rețeta bazat pe conținutul vizual.       │
│                                                              │
│  ─────────────────────────────────────────────────────────  │
│                                                              │
│  Titlu: Sarmale moldovenești                                │
│  Descriere: Sarmale tradiționale cu carne de porc...       │
│  Ingrediente: 15                                            │
│  Pași: 12                                                   │
│  Timp total: 180 minute                                     │
│  Dificultate: Intermediar                                   │
│  Etichete: tradițional, românesc, cină, moderat             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ [Vezi detalii complete]                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Acceptați această rețetă?                                  │
│                                                              │
│     ┌──────────┐      ┌──────────┐      ┌──────────┐       │
│     │   Da     │      │  Editare │      │   Nu     │       │
│     └──────────┘      └──────────┘      └──────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Processing Pipeline

### Step-by-Step Flow

```
User Input (YouTube URLs)
         ↓
   ┌─────────────┐
   │ Validation  │ → Check URL format
   │             │ → Remove duplicates
   │             │ → Extract video IDs
   └─────────────┘
         ↓
   ┌─────────────┐
   │ Send to     │ → Direct YouTube link to Gemini 2.5 Pro
   │ Gemini API  │ → No transcript extraction needed
   │             │ → Gemini processes video content directly
   └─────────────┘
         ↓
   ┌─────────────┐
   │ Gemini      │ → Analyzes video (visual + audio + transcript if available)
   │ Processing  │ → Extracts recipe information
   │             │ → Generates structured JSON
   │             │ → Selects appropriate tags from provided list
   └─────────────┘
         ↓
   ┌─────────────┐
   │ Validation  │ → Check JSON structure
   │             │ → Validate required fields
   │             │ → Verify tags are from predefined list
   │             │ → Ensure units are valid
   └─────────────┘
         ↓
   ┌─────────────┐
   │ User        │ → If video had no transcript: show confirmation
   │ Confirmation│ → Display recipe preview
   │             │ → Allow accept/reject/edit
   └─────────────┘
         ↓
   ┌─────────────┐
   │ Export      │ → Combine all recipes into single JSON array
   │ JSON        │ → Add metadata (generation date, source)
   │             │ → Save to output/recipes_export.json
   └─────────────┘
         ↓
   ┌─────────────┐
   │ Import to   │ → User manually imports in Mealee app
   │ Mealee      │ → Or provide auto-import via Firebase
   └─────────────┘
```

### Processing Logic (Pseudocode)

```python
def process_youtube_urls(urls, api_key, available_tags):
    """
    Main processing function
    """
    recipes = []

    for i, url in enumerate(urls):
        # Update progress
        log_progress(f"Se procesează video {i+1}/{len(urls)}...")

        # Validate URL
        if not is_valid_youtube_url(url):
            log_error(f"URL invalid: {url}")
            continue

        # Send to Gemini
        try:
            recipe_json = call_gemini_api(
                video_url=url,
                available_tags=available_tags,
                api_key=api_key
            )

            # Validate response
            if validate_recipe_structure(recipe_json):

                # Check if confirmation needed
                if recipe_json.get('no_transcript_warning'):
                    confirmed = show_confirmation_dialog(recipe_json)
                    if not confirmed:
                        log_progress(f"✗ Rețeta respinsă de utilizator")
                        continue

                recipes.append(recipe_json)
                log_progress(f"✓ Rețetă generată: {recipe_json['title']}")
            else:
                log_error(f"Structură JSON invalidă pentru {url}")

        except Exception as e:
            log_error(f"Eroare la procesare: {str(e)}")
            continue

    return recipes
```

---

## 5. Gemini API Integration

### API Configuration

```python
# config.py

GEMINI_MODEL = "gemini-2.5-pro-latest"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"

# Generation parameters
GENERATION_CONFIG = {
    "temperature": 0.7,          # Balanced creativity
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,   # Large enough for detailed recipes
    "response_mime_type": "application/json"
}

# Safety settings (permissive for food content)
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]
```

### Gemini Prompt Template

This is the **most critical part** - the prompt must be extremely detailed and precise to generate perfect recipes.

```python
# gemini_service.py

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

## 6. EXEMPLU COMPLET DE OUTPUT AȘTEPTAT

```json
{{
  "recipeId": "a3f12b8c-4d5e-4f6a-b1c2-3d4e5f6a7b8c",
  "title": "Ciorbă de perișoare cu smântână și leuștean",
  "description": "Ciorbă tradițională românească cu perișoare fragede din carne de porc și vită, legume proaspete și borș de casă. Perfectă pentru mesele de familie.",
  "imageUrl": "https://example.com/placeholder.jpg",
  "prepTime": 30,
  "cookTime": 45,
  "totalTime": 75,
  "servings": 6,
  "difficulty": "intermediate",
  "ingredients": [
    {{"name": "carne tocată de porc", "quantity": 300, "unit": "g"}},
    {{"name": "carne tocată de vită", "quantity": 200, "unit": "g"}},
    {{"name": "orez", "quantity": 100, "unit": "g"}},
    {{"name": "ouă", "quantity": 1, "unit": "buc"}},
    {{"name": "ceapă", "quantity": 1, "unit": "buc"}},
    {{"name": "morcov", "quantity": 2, "unit": "buc"}},
    {{"name": "păstârnac", "quantity": 1, "unit": "buc"}},
    {{"name": "țelină", "quantity": 0.25, "unit": "bucată"}},
    {{"name": "ardei gras", "quantity": 1, "unit": "buc"}},
    {{"name": "roșii", "quantity": 2, "unit": "buc"}},
    {{"name": "borș", "quantity": 300, "unit": "ml"}},
    {{"name": "sare", "quantity": 1, "unit": "la gust"}},
    {{"name": "piper negru", "quantity": 1, "unit": "la gust"}},
    {{"name": "leuștean", "quantity": 1, "unit": "legătură"}},
    {{"name": "smântână", "quantity": 200, "unit": "ml"}}
  ],
  "instructions": [
    "Amestecați carnea tocată cu orezul spălat, oul, ceapa tocată fin, sare și piper până obțineți o compoziție omogenă.",
    "Modelați perișoare de mărimea unei nuci și lăsați-le la frigider 15 minute.",
    "Curățați și tăiați toate legumele în cuburi mici (morcov, păstârnac, țelină, ardei).",
    "Puneți 2.5 litri de apă la fiert într-o oală mare.",
    "Când apa clocotește, adăugați legumele tăiate și lăsați să fiarbă 10 minute.",
    "Adăugați perișoarele cu grijă în oală, unul câte unul.",
    "Fierbeți la foc mediu 25-30 minute până când perișoarele plutesc la suprafață.",
    "Adăugați roșiile rase sau tăiate cubulețe și borșul.",
    "Lăsați să mai fiarbă 10 minute, apoi adăugați leușteanul tocat.",
    "Serviți ciorba fierbinte cu smântână și pâine de casă."
  ],
  "nutrition": {{
    "calories": 285,
    "protein": 18,
    "carbs": 22,
    "fats": 14,
    "healthScore": 68
  }},
  "tags": [
    "prânz",
    "tradițional",
    "intermediar",
    "moderat",
    "românesc",
    "pentru familie"
  ],
  "category": "lunch",
  "cuisine": "romanian",
  "createdBy": "youtube_import",
  "createdAt": "2025-11-19T10:30:00Z",
  "isFavorite": false,
  "no_transcript_warning": false
}}
```

# OUTPUT FINAL

Returnează DOAR obiectul JSON, fără text suplimentar, fără markdown code blocks.
Asigură-te că JSON-ul este valid și poate fi parsat direct.
"""

def call_gemini_api(video_url: str, available_tags: list, api_key: str) -> dict:
    """
    Calls Gemini API to extract recipe from YouTube video

    Args:
        video_url: YouTube video URL
        available_tags: List of allowed tags
        api_key: Google Gemini API key

    Returns:
        dict: Recipe JSON object
    """
    import google.generativeai as genai
    import json
    from datetime import datetime

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

    # Send request
    response = model.generate_content([
        prompt,
        {"mime_type": "text/plain", "data": f"YouTube Video: {video_url}"}
    ])

    # Parse JSON response
    recipe_json = json.loads(response.text)

    # Add current timestamp if missing
    if not recipe_json.get('createdAt'):
        recipe_json['createdAt'] = datetime.utcnow().isoformat() + 'Z'

    return recipe_json
```

---

## 6. JSON Output Format

### Final Export Structure

The app will generate a JSON file with this structure:

```json
{
  "metadata": {
    "exportDate": "2025-11-19T10:30:00Z",
    "totalRecipes": 5,
    "source": "youtube_recipe_generator_v1.0",
    "targetApp": "mealee"
  },
  "recipes": [
    {
      "recipeId": "uuid-here",
      "title": "Ciorbă de perișoare",
      ...
    },
    {
      "recipeId": "uuid-here",
      "title": "Sarmale în foi de varză",
      ...
    }
  ]
}
```

### Validation Schema

```python
# recipe_validator.py

import jsonschema

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
        "imageUrl": {"type": "string", "format": "uri"},
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
        "createdAt": {"type": "string", "format": "date-time"},
        "isFavorite": {"type": "boolean"}
    }
}

def validate_recipe(recipe_json: dict, available_tags: list) -> tuple[bool, str]:
    """
    Validates recipe JSON against schema and business rules

    Returns:
        (is_valid, error_message)
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
    if recipe_json['totalTime'] < (recipe_json['prepTime'] + recipe_json['cookTime']):
        return False, "totalTime must be >= prepTime + cookTime"

    # Required tag categories
    meal_tags = {'mic dejun', 'prânz', 'cină', 'gustare', 'desert'}
    if not any(tag in meal_tags for tag in recipe_tags):
        return False, "Must include at least one meal type tag"

    difficulty_tags = {'începător', 'intermediar', 'avansat'}
    if not any(tag in difficulty_tags for tag in recipe_tags):
        return False, "Must include difficulty tag"

    time_tags = {'rapid', 'moderat', 'îndelungat'}
    if not any(tag in time_tags for tag in recipe_tags):
        return False, "Must include time duration tag"

    return True, ""
```

---

## 7. Implementation Steps

### Phase 1: Project Setup (30 minutes)

```bash
# Create project directory
mkdir youtube-recipe-generator
cd youtube-recipe-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create file structure
mkdir assets output
touch main.py gemini_service.py recipe_validator.py config.py
touch requirements.txt README.md

# Download placeholder image
# (Use any generic cooking/recipe image as placeholder.jpg in assets/)
```

### Phase 2: Dependencies Installation (10 minutes)

```python
# requirements.txt

tkinter==8.6  # Usually comes with Python
google-generativeai==0.3.2
jsonschema==4.20.0
requests==2.31.0
python-dotenv==1.0.0
```

```bash
pip install -r requirements.txt
```

### Phase 3: Configuration Module (30 minutes)

```python
# config.py

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
GEMINI_MODEL = "gemini-2.5-pro-latest"
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
    from dotenv import load_dotenv
    load_dotenv(CONFIG_FILE)
    return os.getenv("GEMINI_API_KEY", "")

def save_api_key(api_key: str):
    """Save API key to .env file"""
    with open(CONFIG_FILE, "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
```

### Phase 4: Gemini Service Implementation (2 hours)

See section 5 for complete implementation.

### Phase 5: Recipe Validator (1 hour)

See section 6 for complete implementation.

### Phase 6: GUI Implementation (3 hours)

```python
# main.py

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import threading
import json
from datetime import datetime
from pathlib import Path

from config import *
from gemini_service import call_gemini_api
from recipe_validator import validate_recipe

class YouTubeRecipeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(GUI_TEXT["window_title"])
        self.root.geometry("800x900")
        self.root.resizable(True, True)

        self.recipes = []
        self.processing = False

        self.setup_ui()
        self.load_saved_api_key()

    def setup_ui(self):
        """Create all GUI components"""

        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        current_row = 0

        # === API Key Section ===
        ttk.Label(main_frame, text=GUI_TEXT["api_key_label"], font=("Arial", 10, "bold")).grid(
            row=current_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        current_row += 1

        api_frame = ttk.Frame(main_frame)
        api_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        api_frame.columnconfigure(0, weight=1)

        self.api_key_entry = ttk.Entry(api_frame, show="*", font=("Arial", 10))
        self.api_key_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.save_api_button = ttk.Button(api_frame, text=GUI_TEXT["api_key_save"], command=self.save_api_key)
        self.save_api_button.grid(row=0, column=1)

        current_row += 1

        # === Tags Section ===
        ttk.Label(main_frame, text=GUI_TEXT["tags_label"], font=("Arial", 10, "bold")).grid(
            row=current_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        current_row += 1

        self.tags_text = scrolledtext.ScrolledText(main_frame, height=4, font=("Arial", 9), wrap=tk.WORD)
        self.tags_text.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.tags_text.insert("1.0", ", ".join(AVAILABLE_TAGS))

        current_row += 1

        # === URLs Section ===
        ttk.Label(main_frame, text=GUI_TEXT["urls_label"], font=("Arial", 10, "bold")).grid(
            row=current_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        current_row += 1

        self.urls_text = scrolledtext.ScrolledText(main_frame, height=10, font=("Arial", 10), wrap=tk.WORD)
        self.urls_text.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.urls_text.insert("1.0", GUI_TEXT["urls_placeholder"])
        self.urls_text.bind("<FocusIn>", self.clear_placeholder)

        current_row += 1

        # === Generate Button ===
        self.generate_button = ttk.Button(
            main_frame,
            text=GUI_TEXT["generate_button"],
            command=self.generate_recipes,
            style="Accent.TButton"
        )
        self.generate_button.grid(row=current_row, column=0, pady=(0, 15))

        current_row += 1

        # === Progress Section ===
        ttk.Label(main_frame, text=GUI_TEXT["progress_label"], font=("Arial", 10, "bold")).grid(
            row=current_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        current_row += 1

        self.progress_text = scrolledtext.ScrolledText(main_frame, height=8, font=("Consolas", 9),
                                                       wrap=tk.WORD, state=tk.DISABLED)
        self.progress_text.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Configure tags for colored output
        self.progress_text.tag_config("success", foreground="green")
        self.progress_text.tag_config("error", foreground="red")
        self.progress_text.tag_config("warning", foreground="orange")

        current_row += 1

        # === Action Buttons ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=0, pady=(0, 10))

        self.preview_button = ttk.Button(button_frame, text=GUI_TEXT["preview_button"],
                                        command=self.preview_recipes, state=tk.DISABLED)
        self.preview_button.grid(row=0, column=0, padx=(0, 10))

        self.export_button = ttk.Button(button_frame, text=GUI_TEXT["export_button"],
                                       command=self.export_recipes, state=tk.DISABLED)
        self.export_button.grid(row=0, column=1)

        # Configure row weights for resizing
        for i in range(current_row + 1):
            if i in [4, 7]:  # URLs and Progress areas
                main_frame.rowconfigure(i, weight=1)

    def clear_placeholder(self, event):
        """Clear placeholder text on focus"""
        if self.urls_text.get("1.0", tk.END).strip() == GUI_TEXT["urls_placeholder"].strip():
            self.urls_text.delete("1.0", tk.END)

    def load_saved_api_key(self):
        """Load previously saved API key"""
        api_key = load_api_key()
        if api_key:
            self.api_key_entry.insert(0, api_key)

    def save_api_key(self):
        """Save API key to config file"""
        api_key = self.api_key_entry.get().strip()
        if api_key:
            save_api_key(api_key)
            self.log_progress("✓ Cheie API salvată", "success")
        else:
            messagebox.showwarning("Atenție", "Vă rugăm să introduceți o cheie API validă.")

    def log_progress(self, message: str, tag: str = ""):
        """Add message to progress log"""
        self.progress_text.config(state=tk.NORMAL)
        if tag:
            self.progress_text.insert(tk.END, message + "\n", tag)
        else:
            self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.progress_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def validate_inputs(self) -> tuple[bool, str, list]:
        """Validate user inputs"""
        # Check API key
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            return False, GUI_TEXT["error_no_api_key"], []

        # Get and validate URLs
        urls_text = self.urls_text.get("1.0", tk.END).strip()
        if not urls_text or urls_text == GUI_TEXT["urls_placeholder"].strip():
            return False, GUI_TEXT["error_no_urls"], []

        urls = [line.strip() for line in urls_text.split("\n") if line.strip()]

        # Validate YouTube URLs
        valid_urls = []
        for url in urls:
            if "youtube.com/watch" in url or "youtu.be/" in url:
                valid_urls.append(url)
            else:
                self.log_progress(GUI_TEXT["error_invalid_url"].format(url=url), "error")

        if not valid_urls:
            return False, "Nu s-au găsit URL-uri YouTube valide.", []

        return True, api_key, valid_urls

    def generate_recipes(self):
        """Start recipe generation process"""
        if self.processing:
            return

        # Validate inputs
        is_valid, result, urls = self.validate_inputs()
        if not is_valid:
            messagebox.showerror("Eroare", result)
            return

        api_key = result

        # Get tags
        tags_text = self.tags_text.get("1.0", tk.END).strip()
        available_tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        # Clear previous results
        self.recipes = []
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.delete("1.0", tk.END)
        self.progress_text.config(state=tk.DISABLED)

        # Start processing in background thread
        self.processing = True
        self.generate_button.config(state=tk.DISABLED)

        thread = threading.Thread(
            target=self.process_urls,
            args=(urls, api_key, available_tags),
            daemon=True
        )
        thread.start()

    def process_urls(self, urls: list, api_key: str, available_tags: list):
        """Process YouTube URLs (runs in background thread)"""
        try:
            self.log_progress("Se inițializează Gemini API...")

            for i, url in enumerate(urls, 1):
                self.log_progress(f"\nSe procesează video {i}/{len(urls)}: {url}")

                try:
                    # Call Gemini API
                    recipe_json = call_gemini_api(url, available_tags, api_key)

                    # Validate recipe
                    is_valid, error_msg = validate_recipe(recipe_json, available_tags)

                    if not is_valid:
                        self.log_progress(f"✗ Validare eșuată: {error_msg}", "error")
                        continue

                    # Check if confirmation needed
                    if recipe_json.get('no_transcript_warning', False):
                        # Schedule confirmation dialog on main thread
                        self.root.after(0, lambda r=recipe_json: self.show_confirmation_dialog(r))
                    else:
                        self.recipes.append(recipe_json)
                        self.log_progress(f"✓ Rețetă generată: {recipe_json['title']}", "success")

                except Exception as e:
                    self.log_progress(GUI_TEXT["error_processing"].format(error=str(e)), "error")
                    continue

            # Finished
            self.log_progress(f"\n{GUI_TEXT['success_message'].format(count=len(self.recipes))}", "success")

            # Enable export buttons
            if self.recipes:
                self.root.after(0, self.enable_export_buttons)

        finally:
            self.processing = False
            self.root.after(0, lambda: self.generate_button.config(state=tk.NORMAL))

    def show_confirmation_dialog(self, recipe_json: dict):
        """Show confirmation dialog for recipes without transcript"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title(GUI_TEXT["confirmation_title"])
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Warning message
        warning_label = ttk.Label(dialog, text=GUI_TEXT["confirmation_warning"],
                                 font=("Arial", 10), foreground="orange")
        warning_label.pack(pady=10)

        # Recipe preview
        preview_frame = ttk.Frame(dialog)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, font=("Arial", 9))
        preview_text.pack(fill=tk.BOTH, expand=True)

        # Format recipe preview
        preview_content = f"""
Titlu: {recipe_json['title']}
Descriere: {recipe_json['description']}

Ingrediente: {len(recipe_json['ingredients'])}
Pași: {len(recipe_json['instructions'])}
Timp total: {recipe_json['totalTime']} minute
Dificultate: {recipe_json['difficulty']}
Etichete: {', '.join(recipe_json['tags'])}

Ingrediente detaliate:
"""
        for ing in recipe_json['ingredients']:
            preview_content += f"  - {ing['name']}: {ing['quantity']} {ing['unit']}\n"

        preview_content += "\nInstrucțiuni:\n"
        for i, step in enumerate(recipe_json['instructions'], 1):
            preview_content += f"  {i}. {step}\n"

        preview_text.insert("1.0", preview_content)
        preview_text.config(state=tk.DISABLED)

        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        result = {"accepted": False}

        def accept():
            result["accepted"] = True
            dialog.destroy()

        def reject():
            result["accepted"] = False
            dialog.destroy()

        ttk.Button(button_frame, text=GUI_TEXT["confirmation_accept"],
                  command=accept).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=GUI_TEXT["confirmation_reject"],
                  command=reject).pack(side=tk.LEFT, padx=5)

        # Wait for dialog to close
        dialog.wait_window()

        # Process result
        if result["accepted"]:
            self.recipes.append(recipe_json)
            self.log_progress(f"✓ Rețetă acceptată: {recipe_json['title']}", "success")
        else:
            self.log_progress(f"✗ Rețetă respinsă de utilizator", "warning")

    def enable_export_buttons(self):
        """Enable preview and export buttons"""
        self.preview_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)

    def preview_recipes(self):
        """Show preview of generated recipes"""
        if not self.recipes:
            messagebox.showinfo("Info", "Nu există rețete de previzualizat.")
            return

        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Previzualizare Rețete")
        preview_window.geometry("700x600")

        preview_text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, font=("Arial", 9))
        preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Format all recipes
        preview_content = f"Total rețete: {len(self.recipes)}\n\n"
        preview_content += "=" * 70 + "\n\n"

        for i, recipe in enumerate(self.recipes, 1):
            preview_content += f"REȚETA #{i}\n"
            preview_content += f"Titlu: {recipe['title']}\n"
            preview_content += f"Categorie: {recipe['category']} | Bucătărie: {recipe['cuisine']}\n"
            preview_content += f"Timp: {recipe['totalTime']} min | Porții: {recipe['servings']}\n"
            preview_content += f"Dificultate: {recipe['difficulty']}\n"
            preview_content += f"Etichete: {', '.join(recipe['tags'])}\n"
            preview_content += "\n" + "=" * 70 + "\n\n"

        preview_text.insert("1.0", preview_content)
        preview_text.config(state=tk.DISABLED)

    def export_recipes(self):
        """Export recipes to JSON file"""
        if not self.recipes:
            messagebox.showinfo("Info", "Nu există rețete de exportat.")
            return

        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=OUTPUT_DIR,
            initialfile=f"recipes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if not file_path:
            return

        # Create export structure
        export_data = {
            "metadata": {
                "exportDate": datetime.utcnow().isoformat() + "Z",
                "totalRecipes": len(self.recipes),
                "source": "youtube_recipe_generator_v1.0",
                "targetApp": "mealee"
            },
            "recipes": self.recipes
        }

        # Write to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            self.log_progress(GUI_TEXT["export_success"].format(path=file_path), "success")
            messagebox.showinfo("Succes", f"Rețete exportate cu succes!\n\nFișier: {file_path}")

        except Exception as e:
            self.log_progress(f"✗ Eroare la export: {str(e)}", "error")
            messagebox.showerror("Eroare", f"Eroare la exportul fișierului:\n{str(e)}")

def main():
    root = tk.Tk()
    app = YouTubeRecipeGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

### Phase 7: Testing & Refinement (2 hours)

See section 10 for testing checklist.

---

## 8. Dependencies & Requirements

### Python Version
- **Minimum:** Python 3.8+
- **Recommended:** Python 3.10+

### External Libraries

```
google-generativeai==0.3.2   # Gemini API client
jsonschema==4.20.0           # JSON validation
requests==2.31.0             # HTTP requests
python-dotenv==1.0.0         # Environment variable management
```

### System Requirements
- **OS:** Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 500MB for app + dependencies
- **Internet:** Required for Gemini API calls

### API Requirements
- **Google Gemini API Key**
  - Get from: https://makersuite.google.com/app/apikey
  - Model access: Gemini 2.5 Pro
  - Quota: Recommended 60 requests/minute

---

## 9. Error Handling & Edge Cases

### Error Scenarios & Solutions

| Scenario | Detection | Handling | User Feedback |
|----------|-----------|----------|---------------|
| Invalid API key | HTTP 401 from Gemini | Stop processing, prompt user | "Cheie API invalidă. Verificați și salvați din nou." |
| Rate limit exceeded | HTTP 429 from Gemini | Exponential backoff, retry | "Limită API atinsă. Se reîncearcă în X secunde..." |
| Invalid YouTube URL | URL parsing fails | Skip URL, log error | "URL invalid: {url}" |
| Private/deleted video | Gemini returns error | Skip video, log warning | "Video indisponibil: {url}" |
| No transcript available | Gemini sets flag | Show confirmation dialog | "⚠ Video fără transcriere - verificați rețeta" |
| Invalid JSON response | JSON parse error | Retry once, then skip | "Răspuns invalid de la Gemini" |
| Missing required fields | Schema validation fails | Skip recipe, log details | "Câmpuri obligatorii lipsă: {fields}" |
| Invalid tags | Tag not in allowed list | Remove invalid tags or skip | "Etichete invalide: {tags}" |
| Network timeout | Request timeout > 60s | Retry 3 times, then fail | "Timeout la procesare. Reîncercați." |
| Large batch processing | User cancels operation | Graceful shutdown | "Procesare oprită. Rețete salvate: X/Y" |

### Retry Logic

```python
def call_with_retry(func, max_retries=3, backoff_factor=2):
    """
    Retry function with exponential backoff
    """
    import time

    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            wait_time = backoff_factor ** attempt
            print(f"Retry {attempt + 1}/{max_retries} în {wait_time}s...")
            time.sleep(wait_time)
```

### Input Sanitization

```python
def sanitize_youtube_url(url: str) -> str:
    """
    Extract clean YouTube video URL
    """
    import re

    # Extract video ID
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"

    raise ValueError(f"Invalid YouTube URL: {url}")
```

---

## 10. Testing Checklist

### Unit Tests

- [ ] **Config Module**
  - [ ] API key save/load functionality
  - [ ] Directory creation
  - [ ] Tag list completeness

- [ ] **Validator Module**
  - [ ] Schema validation with valid recipe
  - [ ] Schema validation with missing fields
  - [ ] Tag validation (valid/invalid tags)
  - [ ] Time validation (prepTime + cookTime = totalTime)
  - [ ] Unit validation (valid/invalid units)
  - [ ] Nutrition range validation

- [ ] **Gemini Service**
  - [ ] API key authentication
  - [ ] Request formatting
  - [ ] Response parsing
  - [ ] Error handling (timeout, invalid response)

### Integration Tests

- [ ] **End-to-End Flow**
  - [ ] Single YouTube URL → JSON export
  - [ ] Multiple URLs → batch processing
  - [ ] Mixed valid/invalid URLs
  - [ ] Video without transcript → confirmation dialog

- [ ] **API Integration**
  - [ ] Gemini API call success
  - [ ] Gemini API error handling
  - [ ] Rate limiting behavior
  - [ ] Large response handling

### GUI Tests

- [ ] **Input Validation**
  - [ ] Empty API key → error message
  - [ ] Invalid API key → error message
  - [ ] Empty URL list → error message
  - [ ] Invalid URLs → skip with warning

- [ ] **User Interactions**
  - [ ] API key save/load
  - [ ] Tag editing
  - [ ] URL input (paste, type)
  - [ ] Generate button (enable/disable states)
  - [ ] Progress log updates in real-time
  - [ ] Confirmation dialog accept/reject
  - [ ] Preview window display
  - [ ] Export file save

- [ ] **Threading**
  - [ ] GUI remains responsive during processing
  - [ ] Progress updates from background thread
  - [ ] Cancel operation (if implemented)

### Real-World Test Cases

#### Test Case 1: Simple Recipe Video
```
Input: https://www.youtube.com/watch?v=EXAMPLE1
Expected: Single recipe with Romanian content, valid tags, proper structure
Verify: All required fields present, nutrition realistic, tags from allowed list
```

#### Test Case 2: Multiple Videos (Batch)
```
Input: 5 YouTube URLs
Expected: 5 recipes processed sequentially
Verify: Progress log shows each step, all recipes valid, no data loss
```

#### Test Case 3: Video Without Transcript
```
Input: YouTube video with transcription disabled
Expected: Gemini processes visual content, confirmation dialog shown
Verify: User can accept/reject, recipe still valid if accepted
```

#### Test Case 4: Invalid URLs
```
Input: Mix of valid YouTube URLs and invalid URLs
Expected: Valid URLs processed, invalid URLs skipped with errors
Verify: Error messages clear, processing continues for valid URLs
```

#### Test Case 5: API Rate Limit
```
Scenario: Exceed API quota
Expected: Retry with backoff, clear error message if fails
Verify: User notified, partial results saved
```

### Manual Testing Checklist

Before release, manually test:

- [ ] Install from scratch (fresh Python environment)
- [ ] First-time setup (no saved API key)
- [ ] Process 1 recipe (simple case)
- [ ] Process 10 recipes (stress test)
- [ ] Test with Romanian cooking videos
- [ ] Test with non-Romanian videos (auto-translate)
- [ ] Test with very long videos (>1 hour)
- [ ] Test with very short videos (<5 minutes)
- [ ] Export JSON and import into Mealee app
- [ ] Verify all recipes display correctly in Mealee
- [ ] Check tag filtering works in Mealee
- [ ] Verify nutrition values are reasonable

---

## Additional Notes

### Future Enhancements (V2.0)

1. **Auto-Import to Mealee**
   - Direct Firebase integration
   - Upload recipes without manual JSON import

2. **Image Generation**
   - Use Gemini's image generation for recipe photos
   - Or integrate with Unsplash API for food images

3. **Bulk Processing**
   - YouTube playlist support
   - Channel URL support (process all videos)

4. **Recipe Editing**
   - GUI editor for manual corrections
   - Ingredient substitution suggestions

5. **Multi-Language Support**
   - GUI in multiple languages
   - Recipe content in user's preferred language

6. **Smart Tag Suggestions**
   - ML-based tag recommendations
   - User feedback loop for tag accuracy

7. **Nutrition API Integration**
   - Use USDA FoodData Central for accurate nutrition
   - Ingredient-level nutrition breakdown

### Maintenance Guidelines

- **API Key Security**: Never commit .env file to version control
- **Regular Updates**: Update google-generativeai library monthly
- **Tag Sync**: Keep AVAILABLE_TAGS in sync with Mealee app updates
- **Error Monitoring**: Log all API errors for debugging
- **User Feedback**: Collect feedback on recipe quality and accuracy

### Support & Documentation

- **README.md**: Installation and usage instructions
- **User Guide**: Step-by-step tutorial with screenshots
- **FAQ**: Common issues and solutions
- **Issue Tracker**: GitHub issues for bug reports

---

## Summary

This implementation plan provides a complete blueprint for building a YouTube recipe extraction tool that integrates seamlessly with the Mealee app. The key success factors are:

1. ✅ **Perfect Gemini Prompt**: Detailed, structured, with all validation rules
2. ✅ **Complete Tag System**: All 100+ Mealee tags included
3. ✅ **Romanian Language**: GUI and content fully localized
4. ✅ **Robust Validation**: Schema + business rule validation
5. ✅ **User-Friendly GUI**: Clear progress, confirmations, previews
6. ✅ **Error Handling**: Graceful failures, retry logic, clear feedback
7. ✅ **Direct Import**: JSON format matches Mealee exactly (no manual editing needed)

Follow the implementation phases sequentially, test thoroughly at each stage, and you'll have a production-ready tool for effortless recipe extraction from YouTube videos.

**Estimated Total Development Time:** 8-10 hours

**Technology Stack:** Python 3.10+, Tkinter, Gemini 2.5 Pro API

**License:** MIT (or your preference)

---

*Document Created: 2025-11-19*
*Target Application: Mealee v1.0+*
*Gemini Model: gemini-2.5-pro-latest*
