#!/usr/bin/env python3
"""
Assignment 8 — Voice-controlled AI Image Generator (minimal)

Flow:
  1) Record voice (or use --input audio file)
  2) STT via OpenAI whisper-1 → prompt text
  3) Generate image(s) from the prompt (Pollinations backend by default)
  4) Print URLs and save images into outputs/
  5) Optional TTS confirmation (macOS 'say' fallback)

Usage examples:
  python voice_imggen.py --duration 6 --ratio 16:9 --n 2
  python voice_imggen.py --press-enter --ratio 1:1 --n 1
  python voice_imggen.py --input sample.wav --ratio 3:4 --n 1
"""

import argparse, os, sys, time, platform, shutil, subprocess
from pathlib import Path
from typing import Optional, Tuple, List
import requests
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as wav_write
from openai import OpenAI

# ---------- helpers ----------

RATIO_TO_SIZE = {
    "1:1":  (1024, 1024),
    "16:9": (1280, 720),
    "4:3":  (1024, 768),
    "3:4":  (768, 1024),
}

def pick_size(ratio: str) -> Tuple[int, int]:
    if ratio not in RATIO_TO_SIZE: raise SystemExit(f"ratio must be one of {list(RATIO_TO_SIZE)}")
    return RATIO_TO_SIZE[ratio]

def ts() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def load_env_from_repo_root():
    root_env = Path(__file__).resolve().parents[1] / ".env"
    if root_env.exists():
        for line in root_env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def get_openai_client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        load_env_from_repo_root()
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("ERROR: OPENAI_API_KEY puuttuu (.env).", file=sys.stderr); sys.exit(2)
    return OpenAI(api_key=key)

def speak(text: str):
    # kevyt kuittaus ääneen (valinnainen)
    try:
        if platform.system() == "Darwin" and shutil.which("say"):
            subprocess.Popen(["say", text])
    except Exception:
        pass

# ---------- recording ----------

def record_wav(out_path: Path, duration: Optional[int], press_enter: bool, sr=16000):
    import select
    print(f"[rec] sampling_rate={sr}Hz")
    sd.default.samplerate = sr; sd.default.channels = 1
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
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    sys.stdin.readline()
                    break
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

# ---------- STT ----------

def transcribe_prompt(client: OpenAI, audio_file: Path) -> Tuple[str, float]:
    t0 = time.perf_counter()
    with open(audio_file, "rb") as f:
        tr = client.audio.transcriptions.create(model="whisper-1", file=f)
    dur = time.perf_counter() - t0
    text = tr.text.strip()
    return text, dur

# ---------- image generation (Pollinations) ----------

def pollinations_url(prompt: str, w: int, h: int) -> str:
    from urllib.parse import quote
    return f"https://image.pollinations.ai/prompt/{quote(prompt)}?width={w}&height={h}"

def generate_images_pollinations(prompt: str, ratio: str, n: int, outdir: Path) -> List[Path]:
    w, h = pick_size(ratio)
    print(f"[gen] backend=pollinations ratio={ratio} size={w}x{h} n={n}")
    saved = []
    for i in range(1, n + 1):
        url = pollinations_url(prompt, w, h)
        print(f"[{i}] URL: {url}")
        r = requests.get(url, timeout=120); r.raise_for_status()
        out = outdir / f"vcgen_{ts()}_{i:03d}.png"
        out.write_bytes(r.content)
        print(f"    saved: {out}")
        saved.append(out)
    return saved

# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser(description="Voice-controlled AI Image Generator")
    ap.add_argument("--duration", type=int, default=6, help="Nauhoituksen kesto (s)")
    ap.add_argument("--press-enter", action="store_true", help="ENTER aloita/lopeta nauhoitus")
    ap.add_argument("--input", default=None, help="Valmis audio (WAV/MP3) → ohita nauhoitus")
    ap.add_argument("--ratio", choices=list(RATIO_TO_SIZE.keys()), default="1:1")
    ap.add_argument("--n", type=int, default=1, help="Kuvien määrä")
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    wav_in = outdir / "voice_prompt.wav"

    client = get_openai_client()

    # 1) Record or use file
    if args.input:
        src = Path(args.input)
        if not src.exists(): print(f"ERROR: file not found: {src}", file=sys.stderr); return 2
        wav_in = src
        print(f"[rec] using existing file: {wav_in}")
    else:
        record_wav(wav_in, args.duration if not args.press_enter else None, args.press_enter)

    # 2) STT
    print("[stt] transcribing…")
    prompt, t_stt = transcribe_prompt(client, wav_in)
    print("  prompt:", prompt)
    speak("I will generate images from your voice prompt.")

    # 3) Generate images
    t0 = time.perf_counter()
    images = generate_images_pollinations(prompt, args.ratio, args.n, outdir)
    t_gen = time.perf_counter() - t0

    # 4) Done
    print("\n=== SUMMARY ===")
    print(f"Prompt: {prompt}")
    print(f"Saved files ({len(images)}):")
    for p in images: print(" -", p)
    print(f"Delays: STT={t_stt:.2f}s, IMG={t_gen:.2f}s, TOTAL={(t_stt+t_gen):.2f}s")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
