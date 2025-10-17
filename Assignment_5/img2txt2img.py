#!/usr/bin/env python3
"""
Assignment 5 — Image→Text→Image (minimal CLI)

- Image→Text: OpenAI Vision (gpt-4o)
- Text→Image: OpenAI gpt-image-1 TAI fallback Pollinations (ei avainta)

Käyttö:
  python img2txt2img.py --image path/to/input.jpg
  python img2txt2img.py --image path/to/input.jpg --pollinations --size 1024x682
"""

import argparse, base64, datetime, os, sys, re
from pathlib import Path
from typing import Optional
import requests
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont  # placeholderia varten

# -----------------------
# Helpers
# -----------------------

def b64_data_uri(image_path: Path) -> str:
    ext = image_path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        mime = "image/jpeg"
    elif ext == ".png":
        mime = "image/png"
    elif ext == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"
    b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def describe_image(client: OpenAI, image_path: Path, model: str) -> str:
    """Suomenkielinen, neutraali kuvaus kuvasta."""
    data_uri = b64_data_uri(image_path)
    system = "Olet avustaja, joka kuvailee kuvan ytimekkäästi ja tarkasti suomeksi."
    user_content = [
        {"type": "text", "text": "Kuvaile tämä kuva 3–6 lauseella, neutraalisti ja informatiivisesti."},
        {"type": "image_url", "image_url": {"url": data_uri}},
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

def build_generation_prompt(description_fi: str) -> str:
    """
    Luodaan yksityiskohtainen, Randy Savage -henkinen kuvaus ilman brändi- tai nimiviittauksia.
    """
    base_prompt = (
        "Indoor press interview scene, two people waist-up, 1980s professional wrestling aesthetic. "
        "Left person is a charismatic, muscular man with tanned skin, brown beard, and long wavy hair partially hidden under a patterned headband. "
        "He wears oversized white sunglasses, a colorful tie-dye yellow-red T-shirt with tight sleeves showing muscular arms, "
        "and a bright scarf around his neck. He also wears wristbands, a gold necklace, and holds a ceramic mug in one hand while posing confidently. "
        "Right person is a middle-aged man in a dark suit with a red-and-white striped tie, holding a microphone and looking toward the left person. "
        "Background: blue step-and-repeat backdrop with abstract circular icons, no text, no real logos. "
        "Studio lighting, realistic photo, 1980s broadcast TV atmosphere, slightly saturated colors, high energy expression, both facing each other. "
        "NO animals, NO outdoor scenery, NO fur, NO watermarks or text on the image. "
        "Details from Finnish description: "
    )
    return base_prompt + description_fi


def generate_image_openai(client: OpenAI, prompt: str, model: str, size: str, seed: Optional[int]) -> bytes:
    kwargs = {"model": model, "prompt": prompt, "size": size}
    if seed is not None:
        kwargs["seed"] = seed
    result = client.images.generate(**kwargs)
    b64 = result.data[0].b64_json
    return base64.b64decode(b64)

def generate_image_pollinations(prompt: str, size: str) -> bytes:
    """Text→image Pollinationsista (ei avainta)."""
    try:
        w, h = [int(x) for x in size.lower().split("x")]
    except Exception:
        w, h = 1024, 1024
    url = "https://image.pollinations.ai/prompt/" + requests.utils.quote(prompt)
    url = f"{url}?width={w}&height={h}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content

def save_png(raw: bytes, out_png: Path):
    out_png.write_bytes(raw)

def generate_placeholder(prompt: str, out_png: Path, size: str = "1024x1024"):
    """Hätävara: tekstikuva (ei pitäisi enää tarvita, mutta jätetään varalle)."""
    try:
        w, h = [int(x) for x in size.lower().split("x")]
    except Exception:
        w, h = 1024, 1024
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    text = "Prompt (excerpt):\n" + (prompt[:800] + ("..." if len(prompt) > 800 else ""))
    try:
        font = ImageFont.truetype("Arial.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
    margin, maxw, y = 40, w - 80, 40
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split(" "):
            test = (line + " " + word).strip()
            if draw.textlength(test, font=font) <= maxw:
                line = test
            else:
                draw.text((margin, y), line, fill="black", font=font); y += 34; line = word
                if y > h - margin: img.save(out_png, "PNG"); return
        draw.text((margin, y), line, fill="black", font=font); y += 34
        if y > h - margin: break
    img.save(out_png, "PNG")

# -----------------------
# Main
# -----------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Image→Text→Image (minimal)")
    ap.add_argument("--image", required=True, help="Syötekuvan polku (jpg/png/webp)")
    ap.add_argument("--vision-model", default="gpt-4o", help="Kuvantulkintamalli (oletus gpt-4o)")
    ap.add_argument("--image-model", default="gpt-image-1", help="OpenAI-kuvagenerointimalli")
    ap.add_argument("--size", default="1024x1024", help="Esim. 1024x682 (3:2)")
    ap.add_argument("--outdir", default="outputs", help="Tulostekansio")
    ap.add_argument("--seed", type=int, default=None, help="Siemen (OpenAI)")
    ap.add_argument("--pollinations", action="store_true", help="Pakota Pollinations text→image")
    args = ap.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: Aseta OPENAI_API_KEY ympäristömuuttujaan.", file=sys.stderr)
        return 2

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"ERROR: Tiedostoa ei löydy: {image_path}", file=sys.stderr)
        return 3

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_txt = outdir / f"description_{ts}.txt"
    out_png = outdir / f"generated_{ts}.png"

    client = OpenAI(api_key=api_key)

    try:
        # 1) Image → Text
        description = describe_image(client, image_path, args.vision_model)
        print("\n=== KUVAUS (Image → Text) ===\n"); print(description)
        out_txt.write_text(description, encoding="utf-8")

        # 2) Text → Image (rakennetaan geneerinen, selkeä prompt)
        prompt = build_generation_prompt(description)
        print("\n=== GENEROIDAAN KUVA (Text → Image) ===")

        if args.pollinations:
            img_bytes = generate_image_pollinations(prompt, args.size)
            save_png(img_bytes, out_png)
            print(f"[POLLINATIONS] Valmis: {out_png}")
        else:
            try:
                img_bytes = generate_image_openai(client, prompt, args.image_model, args.size, args.seed)
                save_png(img_bytes, out_png)
                print(f"[OPENAI] Valmis: {out_png}")
            except Exception as e:
                print(f"[WARN] OpenAI image generation failed: {e}\n→ Fallback Pollinations.", file=sys.stderr)
                img_bytes = generate_image_pollinations(prompt, args.size)
                save_png(img_bytes, out_png)
                print(f"[POLLINATIONS] Valmis: {out_png}")

        print(f"\nTallennetut tiedostot:\n- {out_txt}\n- {out_png}")
        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
