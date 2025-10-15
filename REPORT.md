# REPORT.md – Creative Writer CLI

**Tekijä:** Sami Ukkonen  
**GitHub-linkki:** <https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/2f6c826a9d42e272efa538396dda6e83cc52fff5/Assignment%20%233%3A%20Creative%20writer%20command%20line%20app>

## Kuvaus
Komentorivisovellus, joka käyttää OpenAI API:a tuottaakseen SEO-optimoitua luovaa tekstiä.  
Tuottaa oletuksena **3 versiota** samasta promptista. 

## Käyttö
```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install 'openai>=1.40.0,<2.0.0'
export OPENAI_API_KEY="sk-..."
python creative_cli.py --prompt "[prompt]]" \
  --style poem --keywords "black metal, suomalainen, karjala"