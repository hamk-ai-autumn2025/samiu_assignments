# REPORT — Assignment 8: Voice‑controlled AI Image Generator

**Tekijä:** Sami Ukkonen  
**Repo:** https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/main/assignment_8

## Mitä tein
Rakensin minimisovelluksen, joka kuuntelee mikrofonia, muuntaa puheen tekstiksi (OpenAI Whisper‑1) ja käyttää syntyvää tekstiä kuvageneroinnin prompttina (Pollinations). Ohjelma tulostaa generoinnin URLit, lataa kuvat ja tallentaa ne `outputs/`‑kansioon automaattisilla nimillä.

## Miten käytin
```bash
python voice_imggen.py --press-enter --ratio 16:9 --n 2
```
Sanoin englanniksi: *"A whimsical illustration of a green frog taking a bath in a boiling cooking pot on a stove, bubbles and steam. Negative prompt: cat, cats, feline."*

## Tulokset (2 screenshotia)
1. `screenshots/01_cli_run.png` – terminaalin tuloste (prompt, URLit, tallennukset, viiveet).  
2. `screenshots/02_generated_image.png` – avattu tuloskuva (esim. sammakko kattilassa).

## Arvio
- STT osuu hyvin lyhyissä lauseissa; englanti tuottaa parhaan tuloksen Pollinationsissa.
- Kuvasuhteen valinta ja usean kuvan generointi toimivat (1:1, 16:9, 4:3, 3:4; `--n`).
- Negative‑ohje toimii, kun se kirjoitetaan promptin sisään.  
- Vähimmäisvaatimukset täyttyvät: ääni → AI → kuva, URLien tulostus + tiedostojen tallennus.

## Liite: aikaviiveet (esimerkkiajo)
```
STT ≈ 3.5 s, IMG ≈ 8.5 s, TOTAL ≈ 12.0 s
```
