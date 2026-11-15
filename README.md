# 📄 AI PDF Processor

An end-to-end PDF summarizer built with **Streamlit** and **LangChain**, powered by **Google Gemini**.
Upload a PDF, choose a summary style, and get a map-reduce summary plus an optional structure
analysis and key quotes. Results can be downloaded as a text report or a per-chunk CSV.

## Features

- Extracts and cleans text from PDFs, then splits it into token-limited chunks
- Summarizes each chunk, then combines them into one final summary (map-reduce)
- Four summary styles: **brief**, **detailed**, **bullet_points**, **executive**
- Optional document structure analysis and key-quote extraction
- Downloads: summary report (`.txt`) and chunk statistics (`.csv`)
- Per-chunk failure isolation — one failed chunk does not abort the run
- Test suite covering the PDF layer, chains, and exports

## Architecture

```
PDF → extract text → clean → chunk (by tokens)
                                  │
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
             summary 1       summary 2   ...  summary N      (map)
                  └───────────────┼───────────────┘
                                  ▼
                        combine → final summary             (reduce)
```

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI: settings, upload, pipeline run, results, downloads |
| `pdf_processor.py` | PDF text extraction, cleaning, token counting, chunking, metadata |
| `prompts.py` | All `ChatPromptTemplate`s: system message, styles, chunk/combine/analysis/quotes |
| `summarizer.py` | Gemini calls: chunk summaries, combine, analysis, quotes |
| `utils.py` | Display helpers, text/CSV export, time estimate, API-key guard |
| `scripts/make_fixtures.py` | Generates the sample PDFs used by tests and manual checks |
| `tests/` | pytest suite (no API calls) |

## Setup

Requires **Python 3.10+**.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
Copy-Item .env.example .env         # then put your key in .env
```

Get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and set it in `.env`:

```dotenv
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.1-flash-lite
```

`GEMINI_MODEL` sets the default model; it can also be changed in the sidebar.

## Run

```powershell
streamlit run app.py
```

## Tests

```powershell
pip install -r requirements-dev.txt
python scripts/make_fixtures.py
pytest -q
```

The tests mock the LLM, so they do not consume API quota. `scripts/make_fixtures.py` creates:

- `tests/fixtures/short.pdf` — one page, single chunk
- `tests/fixtures/long.pdf` — multi-page, exercises the map-reduce path
- `tests/fixtures/scanned.pdf` — no text layer, exercises the error path

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio API key (required) | — |
| `GEMINI_MODEL` | Default Gemini model | `gemini-3.1-flash-lite` |

`.env` is git-ignored. Never commit real keys. Use `.env.example` as the template.

## Troubleshooting

- **"No extractable text"** — the PDF is probably scanned images; run OCR first.
- **429 / rate limit** — wait a minute, use a smaller document, or switch models.
- **Model not available / 404** — set `GEMINI_MODEL` to a model your key can access.
- **API key not found** — ensure `.env` sits next to `app.py` and defines `GEMINI_API_KEY`.
- **`tiktoken` first run is slow** — it downloads the `cl100k_base` encoding once.

## License

MIT — see [LICENSE](LICENSE).
