# Assignment 7 — Voice Interpreter Program

## Kuvaus
Ohjelma toimii puheentulkkaimena:
1. Nauhoittaa ääntä mikrofonista tai käyttää valmista äänitiedostoa.
2. Muuntaa puheen tekstiksi (**Speech-to-Text**, Whisper-1).
3. Kääntää tekstin toiseen kieleen (**Translation**, GPT-4o-mini).
4. Muuntaa käännöksen takaisin puheeksi (**Text-to-Speech**, GPT-4o-mini-TTS).
5. Tulostaa viiveet ja tallentaa tiedostot kansioon `outputs/`.

## Asennus
```bash
cd assignment_7
python3 -m venv .venv
source .venv/bin/activate
pip install sounddevice scipy openai
```
macOS-käyttäjillä voi olla tarpeen asentaa vielä:
```bash
brew install portaudio
```

Varmista, että repon juuren `.env`-tiedostossa on `OPENAI_API_KEY=...` kuten aiemmissa tehtävissä.

## Käyttö
```bash
# Nauhoita 6 sekuntia englanniksi ja käännä ranskaksi
python voice_interpreter.py --src-lang en --tgt-lang fr --duration 6

# Aloita ja lopeta nauhoitus ENTERillä, käännös suomi → englanti
python voice_interpreter.py --src-lang fi --tgt-lang en --press-enter

# Käytä valmista äänitiedostoa (ohittaa nauhoituksen)
python voice_interpreter.py --input sample.wav --src-lang en --tgt-lang de
```

Tallennetut tiedostot:
```
outputs/input.wav
outputs/output_translated.wav
```

## Esimerkkituloste
```
[rec] sampling_rate=16000Hz
  saved: outputs/input.wav
[stt] transcribing…
  transcript: hello everyone and welcome
[tr] en → fr …
  translation: bonjour à tous et bienvenue
[tts] saved: outputs/output_translated.wav

=== DELAYS (s) ===
STT:        3.12
Translate:  1.07
TTS:        1.21
Total:      5.40
```

## Tekijä
**Sami Ukkonen**  
**Repo:** https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/main/assignment_7
