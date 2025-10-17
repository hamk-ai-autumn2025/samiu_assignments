# Assignment 5 — Image→Text→Image (Minimal CLI)

**Repo (org):** `hamk-ai-autumn2025/samiu_assignments`  
**Kansio:** `Assignment_5`  
**Tekijä / Group:** Sami Ukkonen — group: hamk-ai-autumn2025

## Mitä tämä tekee
1. Lukee paikallisen **kuvatiedoston**.
2. Tekee **kuvauksen** (Image→Text) käyttäen OpenAI:n vision-mallia (oletus `gpt-4o`) ja tulostaa sen konsoliin.
3. Syöttää kuvauksen **promptiksi** text→image -mallille (oletus `gpt-image-1`) ja **generoi uuden kuvan**.

> Huom: Tämä ei ole image-to-image -malli, vaan kaksi erillistä vaihetta (image→text, sitten text→image).

## Asennus (VS Code / venv)
```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here                    # Windows PowerShell: setx OPENAI_API_KEY "key" && $env:OPENAI_API_KEY="key"


## Ajo

python img2txt2img.py --image path/to/kuva.jpg
# Valinn.: --vision-model gpt-4o --image-model gpt-image-1 --size 1024x1024 --seed 123
