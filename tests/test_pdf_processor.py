import pytest

from pdf_processor import PDFProcessor


@pytest.fixture(scope="module")
def processor() -> PDFProcessor:
    return PDFProcessor()


def test_extract_text_from_short_pdf(processor, fixtures_dir):
    with open(fixtures_dir / "short.pdf", "rb") as fh:
        text = processor.extract_text_from_pdf(fh)
    assert "AI PDF Processor sample document" in text


def test_extract_text_from_scanned_pdf_is_empty(processor, fixtures_dir):
    with open(fixtures_dir / "scanned.pdf", "rb") as fh:
        text = processor.extract_text_from_pdf(fh)
    assert text.strip() == ""


def test_clean_text_normalises_whitespace(processor):
    raw = "Hello\t\tworld  \n\n\n\nnext\x00 line"
    assert processor.clean_text(raw) == "Hello world\n\nnext line"


def test_count_tokens_is_positive(processor):
    assert processor.count_tokens("hello world") == 2


def test_chunk_text_rejects_empty_text(processor):
    with pytest.raises(ValueError, match="scanned"):
        processor.chunk_text("   ")


def test_chunk_text_rejects_invalid_max_tokens(processor):
    with pytest.raises(ValueError, match="positive"):
        processor.chunk_text("Some text.", max_tokens=0)


def test_chunks_respect_token_limit(processor):
    sentences = " ".join(f"This is sentence number {i} about a quarterly report." for i in range(200))
    chunks = processor.chunk_text(sentences, max_tokens=40)
    assert len(chunks) > 1
    assert all(processor.count_tokens(c) <= 40 for c in chunks)
    assert "sentence number 0" in chunks[0]
    assert "sentence number 199" in chunks[-1]


def test_oversized_sentence_is_hard_split(processor):
    long_sentence = "word " * 500 + "."
    chunks = processor.chunk_text(long_sentence, max_tokens=25)
    assert len(chunks) > 1
    assert all(processor.count_tokens(c) <= 25 for c in chunks)


def test_metadata_is_read(processor, fixtures_dir):
    with open(fixtures_dir / "short.pdf", "rb") as fh:
        meta = processor.get_pdf_metadata(fh)
    assert meta["num_pages"] == 1
    assert meta["title"] == "Short Sample"
    assert meta["author"] == "AI PDF Processor"
