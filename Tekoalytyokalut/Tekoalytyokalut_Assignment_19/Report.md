# REPORT — Assignment 19: Web Page

**Tekijä:** Sami Ukkonen    
**Repo:** [https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/main/Tekoälytyökalut](https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/main/Tekoälytyökalut)

---

## Kuvaus

Tehtävänä oli luoda yrityksen kotisivun aloitussivu HTML5-muodossa. Sivulla tulee olla yrityksen nimi, osiot kuten *About Us*, *Products*, *Services*, slogan ja lyhyt mainosteksti sekä kuvan paikka. Sivun on oltava responsiivinen ja toimittava mobiililaitteilla. Toteutuksessa sai käyttää AI:ta esimerkiksi sisällön tai kuvan tuottamiseen.

Sivuston aiheeksi valittiin **Möttösen Peruna ja Porkkana**, tahattoman koominen maataloustuottajan “Angelfire-henkinen” kotisivu. Tyyli jäljittelee 1990-luvun varhaista web-estetiikkaa, mutta on teknisesti moderni (Bootstrap 5 + responsiivinen rakenne).

---

## Toteutus

Sivun nimi: **`index.html`**

- **HTML5 + CSS + JS samassa tiedostossa**
- **Bootstrap 5** CDN (responsiivinen layout)
- Retrotyylinen **Comic Sans** -estetiikka ja vilkkuvia efektejä
- Navigaatio: About Us, Products, Services, Contact  
- Hero-osio: slogan + mainosteksti + kuvan paikkamerkki
- **“Generoi retro-maskotti”** -painike, joka hakee kuvan Pollinations.ai-palvelusta (ei vaadi API-avainta)
- Kuvien ja tekstien aiheet AI-luotuja

---

## Käyttö

```bash
# Avaa tiedosto selaimessa
open index.html

# Kuvan vaihtaminen
Klikkaa “Generoi retro-maskotti” → JS hakee uuden AI-kuvan Pollinationsista.