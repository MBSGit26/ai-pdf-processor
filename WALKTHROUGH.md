# PDF AI Processor — Walkthrough

A guide for anyone new to this codebase.

## 1. What the app does

The app takes a PDF, pulls out its text, and asks Google Gemini to summarize it. Long documents are
split into chunks. Each chunk gets its own summary, and the chunk summaries are merged into one final
summary (map-reduce). You pick the model and summary style in the sidebar. You can also turn on a short
structure analysis and a list of key quotes, and download the results.

## 2. Where things are

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI: sidebar settings, upload, pipeline run, results, downloads |
| `prompts.py` | Every LLM instruction: system message, styles, four prompt templates |
| `summarizer.py` | Gemini calls: chunk summaries, combine, structure analysis, quotes |
| `pdf_processor.py` | Reading the PDF, cleaning text, counting tokens, chunking |
| `utils.py` | Results display, text/CSV exports, time estimate, API-key check |
| `tests/` | Unit tests; the LLM is mocked, so no quota is used |

## 3. How a PDF flows through it

1. **Upload** — `st.file_uploader` returns a Streamlit upload object.
2. **Metadata** — `PDFProcessor.get_pdf_metadata()` reads page count, title, author, subject. No LLM call.
3. **Extract** — `extract_text_from_pdf()` runs `page.extract_text()` per page; failed pages are skipped.
4. **Clean** — `clean_text()` drops control characters, squeezes spaces, limits blank lines.
5. **Count** — `count_tokens()` uses tiktoken `cl100k_base` (an approximation of Gemini's tokenizer).
6. **Chunk** — `chunk_text()` splits on sentence boundaries and packs pieces under `max_tokens`.
   A sentence longer than the limit is hard-split by tokens.
7. **Analyze** (optional) — first 3000 characters are sent to the analysis chain.
8. **Summarize chunks** — `chunk_chain.batch(..., max_concurrency=4)`; each failure is recorded,
   not raised.
9. **Combine** — failed chunks are dropped. Zero valid → fixed message. One valid → returned as-is.
   Otherwise the combine chain merges them, falling back to concatenation on error.
10. **Quotes** (optional) — first 5000 characters; numbering/bullets/quotes are stripped, max 10 lines.
11. **Store** — results go into `st.session_state.results` so download clicks (which rerun the script)
    can render them again.
12. **Display / download** — analysis, quotes, statistics, TXT report, CSV of chunk stats.

## 4. Prompt templates

`prompts.py` has a shared `SYSTEM` message and a `STYLES` dict (`brief`, `detailed`, `bullet_points`,
`executive`). The `_template()` helper builds a `ChatPromptTemplate` with the system message plus a
human message.

| Template | Inputs | Purpose |
|---|---|---|
| `CHUNK_SUMMARY` | `{style}`, `{text}` | Summarize one chunk |
| `COMBINE` | `{style}`, `{summaries}` | Merge section summaries, remove repetition |
| `ANALYSIS` | `{text}` | Document type, topics, sections, audience, purpose |
| `QUOTES` | `{text}` | 5–10 verbatim quotes, one per line |

Chains are built with LCEL: `prompt | llm | parser`, where the parser is a `RunnableLambda` returning
`str(message.text)`.

## 5. Extending it

- **New summary style**: add an entry to `STYLES` in `prompts.py`, then add the name to the
  "Summary Type" options in `app.py`.
- **New model**: add it to `MODELS` in `app.py` or set `GEMINI_MODEL` in `.env`.
- **New output**: add a formatter in `utils.py` and a `st.download_button` in `display_results()`.

## 6. Testing strategy

- `tests/test_pdf_processor.py` builds real PDFs with reportlab and checks extraction, cleaning,
  token limits, hard splits, metadata, and empty/scanned input.
- `tests/test_summarizer.py` injects fake chains to test batching, failure isolation, combine
  fallbacks, quote cleanup, and analysis error handling.
- `tests/test_utils.py` checks the text report, CSV dataframe, and time estimate.
