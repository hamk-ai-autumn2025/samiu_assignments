# Assignment 8 — Voice‑controlled AI Image Generator

## Kuvaus
Ääniohjattu ohjelma: puhu prompti → Whisper-1 transkriboi → promptilla generoidaan kuva(t) Pollinations-palvelulla → URLit tulostetaan ja kuvat tallennetaan `outputs/`-kansioon.

## Asennus
```bash
cd assignment_8
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Varmista, että repon juuren `.env` sisältää `OPENAI_API_KEY=...` (Whisperiin).

## Käyttö
```bash
# ENTER aloita/lopeta (helpoin demo), 16:9, 2 kuvaa
python voice_imggen.py --press-enter --ratio 16:9 --n 2

# Kiinteä nauhoitusaika
python voice_imggen.py --duration 6 --ratio 1:1 --n 1

# Ilman mikkiä valmiilla audiolla
python voice_imggen.py --input sample.wav --ratio 3:4 --n 1
```

## Prompt-vinkit
- Puhu tai kirjoita englanniksi selkeästi (subject + action + environment + style).
- Voit lisätä kielteisen ohjauksen prompttiin: `Negative prompt: cat, cats, feline.`

## Tekijä
**Sami Ukkonen**  
**Repo:** https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/main/assignment_8
