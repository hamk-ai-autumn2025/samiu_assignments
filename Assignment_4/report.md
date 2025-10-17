**Nimi:** Sami Ukkonen  
**GitHub-linkki:** <[lisää tähän kurssiorganisaation repo-osoite](https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/f76e0fb86979a6d6bea33f099a28e917f1fcd17a/Assignment_4)>

---

## Kuvaus
Komentorivityökalu, joka syöttää yhden tai useita lähteitä (tekstitiedosto, URL, CSV, DOCX, PDF) suurelle kielimallille (LLM).  
Jos käyttäjä ei anna omaa kysymystä (`--query`), ohjelma tekee **yhteenvedon**.  
Käyttäjä voi myös esittää oman kysymyksen ja rajoittaa vastausten pituutta.

Ympäristömuuttuja `OPENAI_API_KEY` ladataan automaattisesti projektin juuren `.env`-tiedostosta (`python-dotenv`).

---

## Keskeiset ominaisuudet
- Tukee useita lähteitä: `.txt`, `.csv`, `.docx`, `.pdf` ja URL-osoitteet.  
- Yhdistää ja tarvittaessa leikkaa lähteet ennen mallille lähettämistä.  
- Pituuden säätö: `--length short|medium|long` sekä `--max-tokens N`.  
- Lähdekohtaiset rajat: `--per-source-chars` ja `--total-chars`.  
- Oletuksena tulostus komentoriville; valinnaisesti `--out FILE` kirjoittaa tiedostoon.  
- Toimii puhtaassa sessiossa:
  ```bash
  cd Assignment_4
  source .venv/bin/activate
  set -a; source ../.env; set +a
  python mux_cli.py -i gdpr.txt
  ```

---

## Esimerkkiajoja (katso kuvakaappaukset)
1. **Kuvakaappaus A:**  
   ```bash
   python mux_cli.py -i gdpr.txt --length short --max-tokens 200
   ```
   → lyhyt, bulletoitu yhteenveto.

2. **Kuvakaappaus B:**  
   ```bash
   python mux_cli.py \
     -i gdpr.txt -i gdpr.csv -i gdpr.docx \
     -i "https://en.m.wikipedia.org/wiki/General_Data_Protection_Regulation" \
     --length short --max-tokens 200 --per-source-chars 2000 --total-chars 6000
   ```
   → useista lähteistä yhdistetty tiivis yhteenveto.

3. (Valinnainen) Oma kysely ja tiedostoon kirjoitus:
   ```bash
   python mux_cli.py -i gdpr.txt -i gdpr.csv \
     --query "Mitkä ovat 3 tärkeintä asiaa yrityksille käytännössä?" \
     --length medium --max-tokens 300

   python mux_cli.py -i gdpr.txt -i gdpr.docx \
     --length long --max-tokens 800 -o gdpr_summary.txt