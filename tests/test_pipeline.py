from pdf_processor import PDFProcessor
from summarizer import PDFSummarizer
from tests.test_summarizer import make_summarizer


def test_full_pipeline_from_pdf_to_summary(fixtures_dir):
    processor = PDFProcessor()
    with open(fixtures_dir / "short.pdf", "rb") as fh:
        raw = processor.extract_text_from_pdf(fh)

    clean = processor.clean_text(raw)
    chunks = processor.chunk_text(clean, max_tokens=10)
    assert chunks

    summarizer: PDFSummarizer = make_summarizer()
    result = summarizer.summarize_chunks(chunks, "brief")

    assert result["total_chunks"] == len(chunks)
    assert result["combined_summary"] == "combined summary"
    assert all(item["ok"] for item in result["individual_summaries"])
