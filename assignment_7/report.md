# Assignment 7 — Voice Interpreter Program

## Tavoite
Toteuttaa komentoriviltä toimiva tulkkausohjelma, joka yhdistää
puheentunnistuksen (STT), käännöksen (Translation) ja puhesynteesin (TTS).

## Toteutus
Ohjelma on rakennettu Pythonilla ja hyödyntää OpenAI:n rajapintoja:
- **Whisper-1** → puheen muuntaminen tekstiksi
- **GPT-4o-mini** → tekstin kääntäminen toiseen kieleen
- **GPT-4o-mini-TTS** → käännöksen lukeminen ääneen

Tallennus ja toisto toteutettiin kirjastolla **sounddevice** sekä
järjestelmän omilla toistotyökaluilla (macOS → afplay, Linux → aplay).

Lisäksi ohjelma osaa käyttää valmista WAV/MP3-tiedostoa ilman nauhoitusta
ja mittaa eri vaiheiden viiveet.

## Käyttökokemus
Testattu MacBook Pro (macOS Tahoe).
Puheen nauhoitus, transkriptio ja käännös toimivat luotettavasti.
TTS toimii OpenAI-mallilla, ja jos malli ei ole käytettävissä,
järjestelmän oma `say`-komento toimii varavarana.

## Tulokset
Esimerkkiajo (englanti → ranska):
```
[stt] transcribing…
  transcript: good morning everyone
[tr] en → fr …
  translation: bonjour à tous
[tts] saved: outputs/output_translated.wav

=== DELAYS (s) ===
STT:        3.10
Translate:  1.05
TTS:        1.20
Total:      5.35
```
Tulostetut tiedostot:
- outputs/input.wav
- outputs/output_translated.wav

## Arvio onnistumisesta
Prototyyppi täyttää vaatimukset:
- toimii sekä nauhoituksella että valmiilla tiedostolla
- käyttää OpenAI-rajapintoja kolmeen eri tarkoitukseen
- näyttää kokonaisviiveen
- ääni kuuluu onnistuneesti

## Tekijä
**Sami Ukkonen**  
**Repo:** https://github.com/hamk-ai-autumn2025/samiu_assignments/tree/main/assignment_7
