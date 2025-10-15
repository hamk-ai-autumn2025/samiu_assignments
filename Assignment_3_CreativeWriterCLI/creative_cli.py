#!/usr/bin/env python3

# Load .env from project tree root (searches upward)
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True), override=False)
except Exception:
    pass

import os
import sys
import argparse
from openai import OpenAI

DEFAULT_SYSTEM = (
    "You are a creative writer who optimizes for SEO without sounding robotic.\n"
    "Use abundant natural synonyms and related phrases.\n"
    "Weave the given keywords in naturally (no keyword stuffing).\n"
    "Match the requested style: {style}.\n"
    "Return only the content."
)

def main():
    p = argparse.ArgumentParser(description="Minimal SEO creative writer (OpenAI)")
    p.add_argument("--prompt", type=str, help="If omitted, read from stdin")
    p.add_argument("--style", type=str, default="blog",
                   choices=["marketing","meme","lyrics","poem","blog"])
    p.add_argument("--keywords", type=str, default="", help="Comma-separated keywords")
    p.add_argument("--model", type=str, default="gpt-4.1", help="Model name")
    p.add_argument("--system-prompt", type=str, default=DEFAULT_SYSTEM, help="System prompt (may contain {style})")
    p.add_argument("--n", type=int, default=3, help="Number of variants")
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--top-p", type=float, default=1.0)
    p.add_argument("--presence-penalty", type=float, default=0.4)
    p.add_argument("--frequency-penalty", type=float, default=0.3)
    args = p.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: Please set OPENAI_API_KEY", file=sys.stderr)
        sys.exit(2)

    # Get user prompt from arg or stdin
    if args.prompt:
        user_prompt = args.prompt.strip()
    else:
        user_prompt = sys.stdin.read().strip() if not sys.stdin.isatty() else input("Enter your prompt: ").strip()

    # Prepare messages
    system_msg = args.system_prompt.format(style=args.style)
    kw = [k.strip() for k in args.keywords.split(",") if k.strip()]
    kw_line = f"\nTarget keywords: {', '.join(kw)}" if kw else ""
    user_msg = f"{user_prompt}{kw_line}"
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]

    client = OpenAI()

    # Produce variants
    for i in range(args.n):
        resp = client.chat.completions.create(
            model=args.model,
            messages=messages,
            temperature=args.temperature,
            top_p=args.top_p,
            presence_penalty=args.presence_penalty,
            frequency_penalty=args.frequency_penalty,
        )
        text = resp.choices[0].message.content.strip()
        print(f"\n--- Variant {i+1} ---\n{text}")

if __name__ == "__main__":
    main()
