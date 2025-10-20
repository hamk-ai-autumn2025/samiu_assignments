# Tehtävä 5 – Image-to-Text-to-Image -generaattori

**Nimi:** Sami Ukkonen  
**Repository:** [https://github.com/hamk-ai-autumn2025/samiu_assignments](https://github.com/hamk-ai-autumn2025/samiu_assignments)

---

## Tehtävän kuvaus

Ohjelma:
1. Lukee käyttäjän antaman kuvan.  
2. Käyttää tekoälyä (OpenAI GPT-4o) kuvan kuvailemiseen tekstinä.  
3. Käyttää tätä tekstiä uuden kuvan luontiin.  
4. Tulostaa ja tallentaa sekä tekstin että kuvan.

---

## Käytetyt työkalut

- Python 3.12  
- openai, requests, pillow, argparse  
- Pollinations.ai kuvagenerointiin (fallback)  
- .env API-avainta varten

---

## Toiminta

```bash
python img2txt2img.py --image "./Sample image/Randy savage.png" --pollinations --size 1024x682
```

1. Lukee kuvan ja muuntaa sen base64-muotoon.  
2. GPT-4o Vision tekee suomenkielisen kuvauksen.  
3. Ohjelma rakentaa englanninkielisen promptin ja lähettää sen Pollinationsille.  
4. Sekä teksti että kuva tallennetaan `outputs/`-kansioon.

---

## Esimerkkitulokset

**Syötekuva:**  
`Sample image/Randy savage.png`

**AI:n tuottama kuvaus:**  
> Kuvassa on kaksi miestä, joista toinen on pukeutunut värikkääseen, kelta-punaiseen t-paitaan ja aurinkolaseihin. Hänellä on myös värikäs huivi päässään.  
> Toinen mies on pukeutunut tummaan pukuun ja punavalkoraidalliseen solmioon.  
> He pitävät yhdessä kiinni mukista, jossa on mikrofonin pidike.  
> Taustalla on sininen seinä, jossa on toistuva WWF-logo.

**Generoitu kuva:**  
`outputs/generated_20251017-204537.png`

---

## Tulokset

 Kuvan kuvaus oli lyhyt.  
Generoitu kuva vastasi rakenteellisesti ja sisällöllisesti alkuperäistä haastattelutilannetta, mutta paljon korjattavaa olisi
OpenAI-kuvamalli ei ollut käytettävissä, käytettiin Pollinationsia.  

