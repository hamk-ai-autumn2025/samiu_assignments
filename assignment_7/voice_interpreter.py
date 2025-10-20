#!/usr/bin/env python3
"""
Assignment 7 — Voice Interpreter (record → STT → translate → TTS → play)

- Nauhoittaa WAVin TAI lukee valmiin äänitiedoston (--input).
- STT: OpenAI whisper-1
- Käännös: GPT-4o-mini
- TTS: gpt-4o-mini-tts (fallback macOS 'say' jos ei onnistu)
- Tulostaa transkription, käännöksen, tiedostopolut ja viiveet.

Esimerkit:
  python voice_interpreter.py --src-lang en --tgt-lang fr --duration 6
  python voice_interpreter.py --src-lang fi --tgt-lang en --press-enter
  python voice_interpreter.py --input sample.wav --src-lang en --tgt-lang de
"""

import argparse, os, sys, time, subprocess, platform, shutil, select, traceback
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as wav_write
from openai import OpenAI

# ---------- utils ----------

def load_env_from_repo_root():
    root_env = Path(__file__).resolve().parents[1] / ".env"
    if root_env.exists():
        for line in root_env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def get_client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        load_env_from_repo_root()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY puuttuu (.env).", file=sys.stderr)
        sys.exit(2)
    return OpenAI(api_key=api_key)

def play_audio(path: Path) -> bool:
    try:
        if platform.system() == "Darwin" and shutil.which("afplay"):
            subprocess.Popen(["afplay", str(path)])
            return True
        elif platform.system() == "Linux" and shutil.which("aplay"):
            subprocess.Popen(["aplay", str(path)])
            return True
        elif platform.system() == "Windows":
            ps = 'Add-Type –AssemblyName presentationCore; (New-Object System.Media.SoundPlayer "{}").PlaySync()'.format(str(path))
            subprocess.Popen(["powershell", "-c", ps])
            return True
    except Exception:
        return False
    return False

# ---------- Recording ----------

def record_wav(out_path: Path, duration: int | None, press_enter: bool, sr: int = 16000):
    print(f"[rec] sampling_rate={sr}Hz")
    sd.default.samplerate = sr
    sd.default.channels = 1

    if press_enter:
        print("  Paina ENTER aloittaaksesi, ja ENTER lopettaaksesi.")
        input("  ENTER aloittaa…")
        recording = []
        stream = sd.InputStream(samplerate=sr, channels=1, dtype="float32")
        stream.start()
        print("  Nauhoitus käynnissä… (ENTER lopettaa)")
        try:
            while True:
                frames, _ = stream.read(1024)
                recording.append(frames.copy())
                # lopetus kun ENTER painetaan
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    sys.stdin.readline()
                    break
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop(); stream.close()
        audio = np.concatenate(recording, axis=0)
    else:
        print(f"  Nauhoitus {duration}s…")
        audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="float32")
        sd.wait()

    wav = np.int16(np.clip(audio, -1, 1) * 32767)
    wav_write(out_path, sr, wav)
    print(f"  saved: {out_path}")

# ---------- STT / Translate / TTS ----------

def stt_whisper(client: OpenAI, wav_path: Path, src_lang: str | None):
    t0 = time.perf_counter()
    with open(wav_path, "rb") as f:
        tr = client.audio.transcriptions.create(model="whisper-1", file=f)
    dur = time.perf_counter() - t0
    return tr.text.strip(), dur

def translate(client: OpenAI, text: str, src: str, tgt: str):
    t0 = time.perf_counter()
    system = f"You are a precise translator. Translate from {src} to {tgt}. Return only the translation."
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":system},{"role":"user","content":text}],
        temperature=0.2,
    )
    dur = time.perf_counter() - t0
    return resp.choices[0].message.content.strip(), dur

def tts_and_play(client: OpenAI, text: str, out_wav: Path):
    import time, platform, shutil, subprocess
    t0 = time.perf_counter()
    try:
        # HUOM: käytä response_format, ei "format"
        resp = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
            response_format="wav",
        )
        audio_bytes = resp.read()          # luetaan tavut
        out_wav.write_bytes(audio_bytes)   # talletetaan WAV
        dur = time.perf_counter() - t0
        print(f"[tts] saved: {out_wav}")

        # Toista (macOS: afplay)
        played = False
        try:
            if platform.system() == "Darwin" and shutil.which("afplay"):
                subprocess.Popen(["afplay", str(out_wav)])
                played = True
            elif platform.system() == "Linux" and shutil.which("aplay"):
                subprocess.Popen(["aplay", str(out_wav)])
                played = True
            elif platform.system() == "Windows":
                ps = 'Add-Type –AssemblyName presentationCore; (New-Object System.Media.SoundPlayer "{}").PlaySync()'.format(str(out_wav))
                subprocess.Popen(["powershell", "-c", ps]); played = True
        except Exception:
            played = False

        if not played:
            print("  (Vihje: avaa WAV manuaalisesti mediasoittimella.)")
        return dur

    except Exception as e:
        print(f"[tts] OpenAI TTS failed: {e}\n  → fallback to system TTS (macOS 'say' jos saatavilla).", file=sys.stderr)
        dur = time.perf_counter() - t0
        # macOS fallback
        try:
            if platform.system() == "Darwin" and shutil.which("say"):
                subprocess.run(["say", text], check=True)
                return dur
        except Exception:
            pass
        print("  (Ei TTS-toistoa saatavilla. Teksti alla.)")
        print("  SPOKEN:", text)
        return dur


# ---------- Main ----------

def main() -> int:
    ap = argparse.ArgumentParser(description="Voice Interpreter")
    ap.add_argument("--src-lang", default="en")
    ap.add_argument("--tgt-lang", default="fr")
    ap.add_argument("--duration", type=int, default=6)
    ap.add_argument("--press-enter", action="store_true")
    ap.add_argument("--input", default=None, help="Valinnainen olemassa oleva WAV/MP3 → ohita nauhoitus")
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    wav_in  = outdir / "input.wav"
    wav_out = outdir / "output_translated.wav"

    client = get_client()

    # 1) Record or load existing file
    if args.input:
        src = Path(args.input)
        if not src.exists():
            print(f"ERROR: input file not found: {src}", file=sys.stderr)
            return 2
        # ffmpeg/afconvert voisi muuntaa, mutta minimi: luota WAViin tai anna Whisperin lukea suoraan
        wav_in = src
        print(f"[rec] using existing file: {wav_in}")
    else:
        try:
            record_wav(wav_in, None if args.press_enter else args.duration, args.press_enter)
        except Exception as e:
            print("[rec] recording failed:", e, file=sys.stderr)
            return 2

    # 2) STT
    print("[stt] transcribing…")
    try:
        text, t_stt = stt_whisper(client, wav_in, args.src_lang)
    except Exception as e:
        print("[stt] failed:", e, file=sys.stderr)
        return 3
    print("  transcript:", text)

    # 3) Translate
    print(f"[tr] {args.src_lang} → {args.tgt_lang} …")
    try:
        translated, t_tr = translate(client, text, args.src_lang, args.tgt_lang)
    except Exception as e:
        print("[tr] failed:", e, file=sys.stderr)
        return 4
    print("  translation:", translated)

    # 4) TTS
    print("[tts] synthesizing…")
    try:
        t_tts = tts_and_play(client, translated, wav_out)
    except Exception as e:
        print("[tts] failed:", e, file=sys.stderr)
        return 5

    # 5) Delays
    print("\n=== DELAYS (s) ===")
    print(f"STT:        {t_stt:.2f}")
    print(f"Translate:  {t_tr:.2f}")
    print(f"TTS:        {t_tts:.2f}")
    print(f"Total:      {(t_stt + t_tr + t_tts):.2f}")
    print(f"Files: input={wav_in}, tts={wav_out}")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("[fatal] Unexpected error:\n" + "".join(traceback.format_exception(e)), file=sys.stderr)
        raise
