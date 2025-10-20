#!/usr/bin/env python3
"""
Assignment 6 — Versatile Image Generator CLI

Backends:
- pollinations  (default, no API key)
- openai        (requires OPENAI_API_KEY; if it fails, explicit fallback to pollinations)

Features:
- --prompt (required), --negative (best-effort), --seed (if supported),
  --ratio (1:1,16:9,4:3,3:4), --n, --outdir

Prints download URLs (when available) and saves images to --outdir.
"""

import argparse, datetime, os, sys, base64, traceback
from pathlib import Path
from typing import Tuple, List, Optional
import requests

# ----------------- utils -----------------

def ts() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def load_env_from_file(path: Path):
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

RATIO_TO_SIZE = {
    "1:1":  (1024, 1024),
    "16:9": (1280, 720),
    "4:3":  (1024, 768),
    "3:4":  (768, 1024),
}

def pick_size(ratio: str) -> Tuple[int, int]:
    if ratio not in RATIO_TO_SIZE:
        raise SystemExit(f"Unsupported ratio: {ratio}. Use one of {list(RATIO_TO_SIZE)}")
    return RATIO_TO_SIZE[ratio]

# ----------------- OpenAI (optional) -----------------

def get_openai_client():
    try:
        from openai import OpenAI
    except Exception:
        print("[WARN] 'openai' pakettia ei löytynyt. Asenna se tai käytä --backend pollinations.", file=sys.stderr)
        return None
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # yritä lukea repon juuren .env
        load_env_from_file(Path(__file__).resolve().parents[1] / ".env")
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY puuttuu. Käytä --backend pollinations tai aseta avain.", file=sys.stderr)
        return None
    return OpenAI(api_key=api_key)

# ----------------- Pollinations backend -----------------

def pollinations_build_url(prompt: str, negative: Optional[str], w: int, h: int, seed: Optional[int]) -> str:
    from urllib.parse import quote
    p = prompt
    if negative:
        p += f". Negative prompt: {negative}."
    url = "https://image.pollinations.ai/prompt/" + quote(p)
    url += f"?width={w}&height={h}"
    return url

def pollinations_generate(prompt: str, negative: Optional[str], seed: Optional[int],
                          ratio: str, n: int, outdir: Path) -> List[Path]:
    w, h = pick_size(ratio)
    print(f"[gen] backend=pollinations ratio={ratio} size={w}x{h} n={n}")
    out_paths: List[Path] = []
    for i in range(1, n + 1):
        url = pollinations_build_url(prompt, negative, w, h, seed)
        print(f"[{i}] URL: {url}")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        out = outdir / f"gen_{ts()}_{i:03d}.png"
        out.write_bytes(r.content)
        print(f"    saved: {out}")
        out_paths.append(out)
    return out_paths

# ----------------- OpenAI backend -----------------

def openai_generate(prompt: str, negative: Optional[str], seed: Optional[int],
                    ratio: str, n: int, outdir: Path) -> List[Path]:
    client = get_openai_client()
    if client is None:
        print("[INFO] Siirrytään fallbackiin: pollinations.")
        return pollinations_generate(prompt, negative, seed, ratio, n, outdir)

    w, h = pick_size(ratio)
    size = f"{w}x{h}"
    eff_prompt = prompt + (f". Avoid: {negative}." if negative else "")
    print(f"[gen] backend=openai ratio={ratio} size={size} n={n}")

    if seed is not None:
        print("[note] OpenAI Images API ei tue 'seed'-parametria tällä hetkellä; ohitetaan se.")

    out_paths: List[Path] = []
    for i in range(1, n + 1):
        try:
            resp = client.images.generate(
                model="gpt-image-1",
                prompt=eff_prompt,
                size=size,        # HUOM: ei seed-parametria
            )
            b64 = resp.data[0].b64_json
            raw = base64.b64decode(b64)
            out = outdir / f"gen_{ts()}_{i:03d}.png"
            out.write_bytes(raw)
            print(f"[{i}] URL: (binary from OpenAI)")
            print(f"    saved: {out}")
            out_paths.append(out)
        except Exception as e:
            msg = str(e)
            if "must be verified" in msg.lower():
                print("[INFO] OpenAI gpt-image-1 ei käytettävissä (Verified organization vaaditaan).", file=sys.stderr)
            else:
                print(f"[WARN] OpenAI generation failed: {e}", file=sys.stderr)
            print("→ fallback pollinations for this image.")
            out_paths += pollinations_generate(prompt, negative, seed, ratio, 1, outdir)
    return out_paths

# ----------------- main -----------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Versatile Image Generator CLI")
    ap.add_argument("--backend", choices=["pollinations", "openai"], default="pollinations")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative", default=None)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--ratio", choices=list(RATIO_TO_SIZE.keys()), default="1:1")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    print(f"[start] backend={args.backend} prompt='{args.prompt[:60]}' ratio={args.ratio} n={args.n}")
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    try:
        if args.backend == "pollinations":
            paths = pollinations_generate(args.prompt, args.negative, args.seed, args.ratio, args.n, outdir)
        else:
            paths = openai_generate(args.prompt, args.negative, args.seed, args.ratio, args.n, outdir)
        print(f"[done] {len(paths)} image(s) saved to {outdir.resolve()}")
        return 0
    except Exception as e:
        print("[ERROR] Unhandled exception:\n" + "".join(traceback.format_exception(e)), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
