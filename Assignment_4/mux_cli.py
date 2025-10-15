#!/usr/bin/env python3
"""
mux_cli.py — Barebones multi-source → LLM CLI (with output length controls)

Sources: .txt, URL (http/https), .csv, .docx, .pdf
Defaults: if no --query → summarize; output → stdout (or --out FILE)

Env:  OPENAI_API_KEY in env (loaded via python-dotenv if .env present)
Deps: pip install 'openai>=1.40.0,<2.0.0' requests beautifulsoup4 python-docx pypdf python-dotenv
"""

import os, sys, argparse, csv, io, re
from pathlib import Path
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader
from openai import OpenAI

# --- .env support from project root (search upward from CWD) ---
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True), override=False)
except Exception:
    pass

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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
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
            content = read_txt(p)
        label = f"FILE: {p.name}"
    return label, content

def truncate_sources(labeled_texts: List[Tuple[str, str]], per_source_chars: int, total_chars: int):
    trimmed = []
    total = 0
    for label, text in labeled_texts:
        t = text[:per_source_chars]
        if len(text) > per_source_chars:
            t += "\n[...truncated per-source...]"
        if total + len(t) > total_chars:
            remain = max(0, total_chars - total)
            t = t[:remain]
            if remain > 0:
                t += "\n[...truncated global cap...]"
            trimmed.append((label, t))
            break
        trimmed.append((label, t))
        total += len(t)
        if total >= total_chars:
            break
    return trimmed

def build_messages(query: str, labeled_texts: List[Tuple[str, str]], length_hint: str):
    sources_block = "\n\n".join(
        f"=== {label} ===\n{text}" for (label, text) in labeled_texts
    )
    if query:
        user_content = f"Answer the following query using the sources.\nQuery: {query}\n\nSources:\n{sources_block}"
    else:
        user_content = f"Summarize the following sources. Capture only the most important points.\n\nSources:\n{sources_block}"
    length_instruction = {
        "short": "Keep the answer very brief (bulleted, ~5–8 lines).",
        "medium": "Be concise (short paragraphs, ~10–15 lines).",
        "long": "Provide a fuller answer, but avoid fluff."
    }[length_hint]
    system_content = (
        "You are a concise analyst. Cite source labels inline when useful (e.g., [URL:..., FILE:...]). "
        f"{length_instruction} If information is missing, say so briefly."
    )
    return [{"role": "system", "content": system_content},
            {"role": "user", "content": user_content}]

def main():
    ap = argparse.ArgumentParser(description="Multi-source → LLM (barebones, length controls)")
    ap.add_argument("-i", "--input", action="append", required=True,
                    help="Source (repeatable): file (.txt/.csv/.docx/.pdf) or URL")
    ap.add_argument("-q", "--query", type=str, default=None,
                    help="Custom query for the LLM. If omitted → summarize.")
    ap.add_argument("-o", "--out", type=str, default=None,
                    help="Write result to file. Default: stdout.")
    ap.add_argument("--model", type=str, default="gpt-4.1")
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--top-p", type=float, default=1.0)

    # length + token & truncation controls
    ap.add_argument("--length", choices=["short","medium","long"], default="medium",
                    help="High-level length control (default: medium)")
    ap.add_argument("--max-tokens", type=int, default=None,
                    help="Hard cap for model output tokens (overrides --length preset)")
    ap.add_argument("--per-source-chars", type=int, default=4000,
                    help="Max characters per source before sending to LLM")
    ap.add_argument("--total-chars", type:int, default=12000,
                    help="Global max characters across all sources")

    args = ap.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: set OPENAI_API_KEY", file=sys.stderr)
        sys.exit(2)

    labeled_texts = []
    for src in args.input:
        try:
            labeled_texts.append(load_source(src))
        except Exception as e:
            print(f"WARNING: skipping {src}: {e}", file=sys.stderr)

    if not labeled_texts:
        print("No readable sources.", file=sys.stderr)
        sys.exit(1)

    labeled_texts = truncate_sources(labeled_texts, args.per_source_chars, args.total_chars)
    messages = build_messages(args.query, labeled_texts, args.length)

    length_to_tokens = {"short": 250, "medium": 700, "long": 1400}
    max_tokens = args.max_tokens if args.max_tokens is not None else length_to_tokens[args.length]

    client = OpenAI()
    resp = client.chat.completions.create(
        model=args.model,
        messages=messages,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=max_tokens,
    )
    out = resp.choices[0].message.content.strip()

    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    else:
        print(out)

if __name__ == "__main__":
    main()
