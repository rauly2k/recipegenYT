# YouTube Recipe Generator

Aplicație desktop pentru extragerea automată a rețetelor culinare din videoclipuri YouTube, folosind Google Gemini 2.0 Flash API. Rețetele sunt exportate în format JSON pentru import direct în aplicația Mealee.

## 📋 Caracteristici

- ✅ Interfață grafică în limba română
- ✅ Procesare automată a videoclipurilor YouTube
- ✅ Extragere structurată de rețete folosind Google Gemini 2.0 Flash
- ✅ Validare completă a datelor (ingrediente, timpi, etichete)
- ✅ Suport pentru procesare în batch (multiple video-uri simultan)
- ✅ Preview și confirmare înainte de export
- ✅ Export JSON compatibil cu Mealee app
- ✅ 100+ etichete predefinite pentru categorizare

## 🚀 Instalare

### Cerințe de sistem

- Python 3.8 sau mai nou
- Conexiune la internet (pentru API Gemini)
- Sistem de operare: Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)

### Pași de instalare

1. **Clonează repository-ul**

```bash
git clone https://github.com/yourusername/recipegenYT.git
cd recipegenYT
```

2. **Creează un mediu virtual (recomandat)**

```bash
python -m venv venv

# Pe Windows:
venv\Scripts\activate

# Pe macOS/Linux:
source venv/bin/activate
```

3. **Instalează dependențele**

```bash
pip install -r requirements.txt
```

4. **Obține o cheie API Google Gemini**

- Vizitează: https://aistudio.google.com/app/apikey
- Creează un cont Google (dacă nu ai deja)
- Generează o cheie API nouă
- Copiază cheia API (va începe cu `AIzaSy...`)

## 📖 Utilizare

### Pornirea aplicației

```bash
python main.py
```

### Pași de utilizare

1. **Configurează cheia API**
   - Introdu cheia API Gemini în câmpul "Cheia API Gemini"
   - Apasă butonul "Salvează" (cheia va fi salvată local în `.env`)

2. **Adaugă link-uri YouTube**
   - În zona de text "Link-uri YouTube", introdu unul sau mai multe URL-uri
   - Câte un URL pe linie
   - Exemple de formate acceptate:
     - `https://www.youtube.com/watch?v=VIDEO_ID`
     - `https://youtu.be/VIDEO_ID`

3. **Personalizează etichetele (opțional)**
   - În zona "Etichete Disponibile" poți edita lista de taguri
   - Tagurile sunt separate prin virgulă
   - Lista este pre-populată cu toate tagurile din Mealee

4. **Generează rețete**
   - Apasă butonul "Generează Rețete"
   - Urmărește progresul în zona de log
   - Dacă un video nu are transcriere, vei fi întrebat să confirmi rețeta

5. **Previzualizează și exportă**
   - Apasă "Previzualizare" pentru a vedea rețetele generate
   - Apasă "Exportă JSON" pentru a salva rețetele
   - Alege locația și numele fișierului

6. **Import în Mealee**
   - Folosește fișierul JSON exportat pentru import în aplicația Mealee

## 📁 Structura proiectului

```
recipegenYT/
│
├── main.py                      # Aplicația GUI principală
├── gemini_service.py            # Integrare cu Gemini API
├── recipe_validator.py          # Validare JSON schema
├── config.py                    # Configurații și constante
├── requirements.txt             # Dependențe Python
├── README.md                    # Documentație
│
├── assets/                      # Resurse (imagini, etc.)
├── output/                      # Fișiere JSON exportate
├── .env                         # Cheie API (generat automat)
│
└── YOUTUBE_RECIPE_GENERATOR_PLAN.md  # Plan detaliat de implementare
```

## 🔧 Configurare avansată

### Modificarea modelului Gemini

În `config.py`, poți schimba modelul folosit:

```python
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Model implicit
# Alternative:
# GEMINI_MODEL = "gemini-1.5-pro"
# GEMINI_MODEL = "gemini-1.5-flash"
```

### Ajustarea parametrilor de generare

```python
GENERATION_CONFIG = {
    "temperature": 0.7,          # Creativitate (0.0-1.0)
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}
```

### Adăugarea de noi etichete

Editează lista `AVAILABLE_TAGS` din `config.py`:

```python
AVAILABLE_TAGS = [
    # Adaugă tagurile tale aici
    "vegan",
    "fără gluten",
    # ...
]
```

## 🐛 Depanare

### Eroare: "Cheie API invalidă"

- Verifică că ai copiat cheia API corect
- Asigură-te că cheia începe cu `AIzaSy`
- Verifică că API-ul Gemini este activat în contul tău Google Cloud

### Eroare: "Module not found"

```bash
# Reinstalează dependențele
pip install -r requirements.txt --upgrade
```

### Eroare: "tkinter nu este instalat"

```bash
# Ubuntu/Debian:
sudo apt-get install python3-tk

# macOS (folosind Homebrew):
brew install python-tk

# Windows: reinstalează Python cu opțiunea "tcl/tk and IDLE"
```

### Videoclipul nu este procesat corect

- Verifică că URL-ul YouTube este valid
- Unele videoclipuri private sau restricționate nu pot fi procesate
- Videoclipurile foarte lungi (>2 ore) pot dura mai mult

### Rețeta generată are erori

- Verifică că lista de etichete este corectă
- Gemini face estimări pentru informații lipsă
- Poți respinge rețeta și încerca din nou

## 📊 Format JSON Export

Fișierul exportat are următoarea structură:

```json
{
  "metadata": {
    "exportDate": "2025-11-19T10:30:00Z",
    "totalRecipes": 3,
    "source": "youtube_recipe_generator_v1.0",
    "targetApp": "mealee"
  },
  "recipes": [
    {
      "recipeId": "uuid-here",
      "title": "Ciorbă de perișoare",
      "description": "Ciorbă tradițională românească...",
      "prepTime": 30,
      "cookTime": 45,
      "totalTime": 75,
      "servings": 6,
      "difficulty": "intermediate",
      "ingredients": [...],
      "instructions": [...],
      "nutrition": {...},
      "tags": [...],
      "category": "lunch",
      "cuisine": "romanian",
      ...
    }
  ]
}
```

## 🤝 Contribuții

Contribuțiile sunt binevenite! Pentru a contribui:

1. Fork repository-ul
2. Creează un branch pentru feature-ul tău (`git checkout -b feature/amazing-feature`)
3. Commit modificările (`git commit -m 'Add amazing feature'`)
4. Push la branch (`git push origin feature/amazing-feature`)
5. Deschide un Pull Request

## 📝 Licență

Acest proiect este licențiat sub licența MIT - vezi fișierul `LICENSE` pentru detalii.

## 🙏 Mulțumiri

- Google Gemini API pentru procesarea video-urilor
- Comunitatea open-source Python
- Aplicația Mealee pentru inspirație

## 📧 Contact

Pentru întrebări sau sugestii, deschide un issue pe GitHub.

## 🔮 Funcționalități viitoare (V2.0)

- [ ] Import automat în Mealee (integrare Firebase)
- [ ] Generare automată de imagini pentru rețete
- [ ] Suport pentru playlist-uri YouTube
- [ ] Editor GUI pentru editarea manuală a rețetelor
- [ ] Multi-limbă (UI și conținut)
- [ ] Integrare cu baze de date nutriționale (USDA)
- [ ] Sugestii inteligente de taguri folosind ML

---

**Versiune:** 1.0.0
**Data ultimei actualizări:** 2025-11-19
**Python:** 3.8+
**Model Gemini:** gemini-2.0-flash-exp
