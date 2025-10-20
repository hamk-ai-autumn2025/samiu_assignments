# REPORT — Assignment 6

**Nimi:** Sami Ukkonen  
**Repo:** https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/main/assignment_6

## Mitä tein
Rakensin komentorivityökalun (`imggen_cli.py`), joka generoi kuvia kahdella backendilla:
- **Pollinations** (oletus, ei vaadi avainta)
- **OpenAI** (valinnainen; jos ei käytettävissä → automaattinen fallback Pollinationsiin)

CLI tukee: `--prompt`, `--negative` (best-effort), `--ratio {1:1,16:9,4:3,3:4}`, `--n`, `--outdir`.  
OpenAI-seed ei ole tuettu → ohitetaan siististi.

## Ajoesimerkit
```bash
python imggen_cli.py --prompt "cinematic sunrise over pine forest" --ratio 16:9 --n 2
python imggen_cli.py --backend openai --prompt "studio portrait of a friendly robot" --negative "humanlike" --ratio 1:1 --n 1
