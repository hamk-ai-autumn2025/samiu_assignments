#!/usr/bin/env python3

# Load .env from project root (search upwards)
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True), override=False)
except Exception:
    pass

import os, sys, argparse, csv, io, re
from pathlib import Path
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader
from openai import OpenAI

MAX_CHARS_PER_SOURCE = 2000  # yksinkertainen raja ettei prompt paisu liikaa

def is_url(s: str) -> bool:
    return s.lower().startswith(("http://", "https://"))

def read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def read_csv_file(path: Path) -> str:
    out = io.StringIO()
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            out.write(" | ".join(row) + "\n")
    return out.getvalue()

def read_docx_file(path: Path) -> str:
    doc = DocxDocument(path)
    return "\n".join(p.text for p in doc.paragraphs)

def read_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            pass
    return "\n".join(texts)

def read_url(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0 Safari/537.36"
    }
    r = requests.get(url, timeout=20, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    text = soup.get_text(" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_source(src: str) -> Tuple[str, str]:
    """Palauttaa (label, text)."""
    if is_url(src):
        content = read_url(src)
        label = f"URL: {src}"
    else:
        p = Path(src)
        if not p.exists():
            raise FileNotFoundError(f"Not found: {src}")
        ext = p.suffix.lower()
        if ext == ".txt":
            content = read_txt(p)
        elif ext == ".csv":
            content = read_csv_file(p)
        elif ext == ".docx":
            content = read_docx_file(p)
        elif ext == ".pdf":
            content = read_pdf_file(p)
        else:
            # fallback: lue tekstinä
            content = read_txt(p)
        label = f"FILE: {p.name}"
    if len(content) > MAX_CHARS_PER_SOURCE:
        content = content[:MAX_CHARS_PER_SOURCE] + "\n[...truncated...]"
    return label, content

def build_messages(query: str, labeled_texts: List[Tuple[str, str]]):
    sources_block = "\n\n".join(
        f"=== {label} ===\n{text}" for (label, text) in labeled_texts
    )
    if query:
        user_content = f"Answer the following query using the sources.\nQuery: {query}\n\nSources:\n{sources_block}"
    else:
        user_content = f"Summarize the following sources. Capture main points, key facts, and contradictions.\n\nSources:\n{sources_block}"
    system_content = (
        "You are a concise analyst. Cite source labels inline when useful (e.g., [URL:..., FILE:...]). "
        "If information is missing, say so briefly."
    )
    return [{"role": "system", "content": system_content},
            {"role": "user", "content": user_content}]

def main():
    ap = argparse.ArgumentParser(description="Multi-source → LLM (barebones)")
    ap.add_argument("-i", "--input", action="append", required=True,
                    help="Lähde (voi toistua): tiedostopolku (.txt/.csv/.docx/.pdf) tai URL")
    ap.add_argument("-q", "--query", type=str, default=None,
                    help="Kysymys LLM:lle. Jos puuttuu → summarize.")
    ap.add_argument("-o", "--out", type=str, default=None,
                    help="Kirjoita tulos tiedostoon. Oletus: stdout.")
    ap.add_argument("--model", type=str, default="gpt-4.1",
                    help="OpenAI-malli, esim. gpt-4.1, gpt-4o")
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--top-p", type=float, default=1.0)
    args = ap.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: set OPENAI_API_KEY", file=sys.stderr)
        sys.exit(2)

    # Lataa kaikki lähteet
    labeled_texts = []
    for src in args.input:
        try:
            labeled_texts.append(load_source(src))
        except Exception as e:
            print(f"WARNING: skipping {src}: {e}", file=sys.stderr)

    if not labeled_texts:
        print("No readable sources.", file=sys.stderr)
        sys.exit(1)

    messages = build_messages(args.query, labeled_texts)
    client = OpenAI()
    resp = client.chat.completions.create(
        model=args.model,
        messages=messages,
        temperature=args.temperature,
        top_p=args.top_p,
    )
    out = resp.choices[0].message.content.strip()

    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    else:
        print(out)

if __name__ == "__main__":
    main()