Tuottaa oletuksena 3 versiota samasta promptista. Käyttää OpenAI API:a. SEO-tyyli: paljon luonnollisia synonyymejä.

## Ajo
```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install 'openai>=1.40.0'
export OPENAI_API_KEY=sk-...
python creative_cli.py --prompt "Kirjoita vanhoja karjalaisia sananlaskuja suomalaisesta blackmetal teemoista" --style runo --keywords "black metal, suomalainen, karjala"
