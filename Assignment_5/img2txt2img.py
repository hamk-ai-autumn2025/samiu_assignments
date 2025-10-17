#!/usr/bin/env python3
"""
Image→Text→Image (minimal CLI)

- Lukee paikallisen kuvatiedoston (--image).
- Kuvailee sen tekstiksi OpenAI Vision -mallilla (oletus: gpt-4o).
- Tulostaa kuvauksen stdoutiin ja tallentaa sen .txt-tiedostoon.
- Syöttää kuvauksen promptiksi kuvagenerointiin (gpt-image-1) ja tallentaa PNG:n.

Käyttö:
  python img2txt2img.py --image path/to/input.jpg
"""

import argparse, base64, datetime, os, sys, textwrap
from pathlib import Path
from typing import Tuple
from openai import OpenAI

def b64_data_uri(image_path: Path) -> str:
    mime = "image/png"
    if image_path.suffix.lower() in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif image_path.suffix.lower() in [".webp"]:
        mime = "image/webp"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def describe_image(client: OpenAI, image_path: Path, model: str, lang: str = "fi") -> str:
    """Palauttaa lyhyen, selkeän kuvauksen kuvasta."""
    data_uri = b64_data_uri(image_path)
    system = f"Olet avustaja, joka kuvailee kuvat ytimekkäästi ja tarkasti suomeksi."
    user_content = [
        {"type": "text", "text": "Kuvaile tämä kuva 3–6 lauseella, neutraalisti ja informatiivisesti."},
        {"type": "image_url", "image_url": {"url": data_uri}},
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system","content": system},
            {"role":"user","content": user_content},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

def generate_image(client: OpenAI, prompt: str, model: str, size: str, out_png: Path, seed: int | None):
    """Generoi kuvan text→image -mallilla ja tallentaa PNG:n."""
    kwargs = {"model": model, "prompt": prompt, "size": size}
    if seed is not None:
        kwargs["seed"] = seed
    result = client.images.generate(**kwargs)
    b64 = result.data[0].b64_json
    png = base64.b64decode(b64)
    out_png.write_bytes(png)

def main() -> int:
    ap = argparse.ArgumentParser(description="Image→Text→Image (minimal)")
    ap.add_argument("--image", required=True, help="Syötekuvan polku (jpg/png/webp)")
    ap.add_argument("--vision-model", default="gpt-4o", help="Kuvantulkintamalli (oletus gpt-4o)")
    ap.add_argument("--image-model", default="gpt-image-1", help="Kuvagenerointimalli (oletus gpt-image-1)")
    ap.add_argument("--size", default="1024x1024", help="Generoitu kuvan koko (esim. 512x512, 1024x1024)")
    ap.add_argument("--outdir", default="outputs", help="Tulostekansio")
    ap.add_argument("--seed", type=int, default=None, help="Valinnainen siemen luvulle (toistettavuus)")
    args = ap.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: Aseta OPENAI_API_KEY ympäristömuuttujaan.", file=sys.stderr)
        return 2

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"ERROR: Tiedostoa ei löydy: {image_path}", file=sys.stderr)
        return 3

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_txt = outdir / f"description_{ts}.txt"
    out_png = outdir / f"generated_{ts}.png"

    client = OpenAI(api_key=api_key)

    # 1) Image → Text
    description = describe_image(client, image_path, args.vision_model)
    print("\n=== KUVAUS (Image → Text) ===\n")
    print(description)
    out_txt.write_text(description, encoding="utf-8")

    # 2) Text → Image
    # Lisätään kevyt ohjaus, jotta prompt toimii järkevästi text→image -mallissa.
    prompt = (
    "Generate a high-quality image that matches this Finnish description. "
    "Keep the composition faithful to the description.\n\n"
    "Description (Finnish):\n"
    f"{description}"
)
