"""Live end-to-end smoke test: PDF -> Gemini -> summary.

Uses a small amount of API quota. Run after setting GEMINI_API_KEY in .env:

    python scripts/smoke_test.py
    python scripts/smoke_test.py --pdf tests/fixtures/long.pdf --max-tokens 800
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pdf_processor import PDFProcessor  # noqa: E402
from summarizer import PDFSummarizer  # noqa: E402

load_dotenv(ROOT / ".env")


def run(pdf_path: Path, max_tokens: int, summary_type: str, quotes: bool) -> int:
    if not pdf_path.exists():
        print(f"Missing {pdf_path}. Run: python scripts/make_fixtures.py")
        return 1

    processor = PDFProcessor()
    with open(pdf_path, "rb") as fh:
        raw = processor.extract_text_from_pdf(fh)

    clean = processor.clean_text(raw)
    chunks = processor.chunk_text(clean, max_tokens=max_tokens)
    print(f"{pdf_path.name}: {len(clean)} chars -> {len(chunks)} chunk(s)")

    summarizer = PDFSummarizer()
    print(f"Model: {summarizer.model}")

    result = summarizer.summarize_chunks(chunks, summary_type)
    ok = sum(1 for s in result["individual_summaries"] if s["ok"])
    print(f"Chunk summaries ok: {ok}/{result['total_chunks']}")

    print("\n--- FINAL SUMMARY ---")
    print(result["combined_summary"])

    analysis = summarizer.analyze_document_structure(clean)
    print("\n--- ANALYSIS ---")
    print(analysis["analysis"][:400])

    if quotes:
        extracted = summarizer.extract_key_quotes(clean[:5000])
        print(f"\n--- KEY QUOTES ({len(extracted)}) ---")
        for quote in extracted:
            print(f"- {quote}")

    if not result["combined_summary"].strip():
        print("\nFAILED: empty summary")
        return 1
    print("\nOK: smoke test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default=str(ROOT / "tests" / "fixtures" / "short.pdf"))
    parser.add_argument("--max-tokens", type=int, default=2000)
    parser.add_argument("--type", default="brief", choices=["brief", "detailed", "bullet_points", "executive"])
    parser.add_argument("--quotes", action="store_true")
    args = parser.parse_args()
    return run(Path(args.pdf), args.max_tokens, args.type, args.quotes)


if __name__ == "__main__":
    raise SystemExit(main())
