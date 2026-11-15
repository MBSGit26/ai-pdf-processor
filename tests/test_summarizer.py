import pytest

from summarizer import PDFSummarizer


class FakeChain:
    """Minimal stand-in for a LangChain Runnable (invoke + batch)."""

    def __init__(self, fn):
        self.fn = fn

    def invoke(self, value):
        return self.fn(value)

    def batch(self, inputs, config=None, return_exceptions=False):
        results = []
        for item in inputs:
            try:
                results.append(self.fn(item))
            except Exception as exc:  # noqa: BLE001
                if not return_exceptions:
                    raise
                results.append(exc)
        return results


def make_summarizer(chunk_fn=None, combine_fn=None, analysis_fn=None, quotes_fn=None) -> PDFSummarizer:
    summarizer = PDFSummarizer.__new__(PDFSummarizer)
    summarizer.model = "fake-model"
    summarizer.chunk_chain = FakeChain(chunk_fn or (lambda x: f"summary of {len(x['text'])} chars"))
    summarizer.combine_chain = FakeChain(combine_fn or (lambda x: "combined summary"))
    summarizer.analysis_chain = FakeChain(analysis_fn or (lambda x: "analysis"))
    summarizer.quotes_chain = FakeChain(quotes_fn or (lambda x: '"First quote"\n2. Second quote'))
    return summarizer


def test_summarize_chunks_returns_one_entry_per_chunk():
    summarizer = make_summarizer()
    result = summarizer.summarize_chunks(["alpha", "beta", "gamma"], "brief")

    assert result["total_chunks"] == 3
    assert result["summary_type"] == "brief"
    assert [s["chunk_number"] for s in result["individual_summaries"]] == [1, 2, 3]
    assert all(s["ok"] for s in result["individual_summaries"])
    assert result["combined_summary"] == "combined summary"


def test_failed_chunk_is_isolated_and_marked():
    def chunk_fn(item):
        if item["text"] == "bad":
            raise RuntimeError("quota exceeded")
        return "ok summary"

    summarizer = make_summarizer(chunk_fn=chunk_fn)
    result = summarizer.summarize_chunks(["good", "bad"], "detailed")

    ok = [s["ok"] for s in result["individual_summaries"]]
    assert ok == [True, False]
    assert "quota exceeded" in result["individual_summaries"][1]["summary"]


def test_combine_returns_single_summary_without_llm_call():
    def boom(_):
        raise AssertionError("combine_chain should not be called")

    summarizer = make_summarizer(combine_fn=boom)
    summaries = [{"summary": "only one", "ok": True}]
    assert summarizer.combine_summaries(summaries, "brief") == "only one"


def test_combine_with_no_valid_summaries():
    summarizer = make_summarizer()
    summaries = [{"summary": "failed", "ok": False}]
    assert summarizer.combine_summaries(summaries, "brief") == "No valid summaries were generated."


def test_combine_falls_back_when_llm_fails():
    def boom(_):
        raise RuntimeError("network down")

    summarizer = make_summarizer(combine_fn=boom)
    summaries = [{"summary": "one", "ok": True}, {"summary": "two", "ok": True}]
    result = summarizer.combine_summaries(summaries, "brief")
    assert result.startswith("Combined Summary:")
    assert "Section 1: one" in result and "Section 2: two" in result


def test_extract_key_quotes_cleans_lines_and_caps_at_ten():
    raw = "\n".join([f'{i}. "Quote {i}"' for i in range(1, 13)])
    summarizer = make_summarizer(quotes_fn=lambda _: raw)
    quotes = summarizer.extract_key_quotes("text")

    assert len(quotes) == 10
    assert quotes[0] == "Quote 1"


def test_analyze_document_structure_success_and_error():
    summarizer = make_summarizer(analysis_fn=lambda _: "a report")
    assert summarizer.analyze_document_structure("text") == {"analysis": "a report", "status": "success"}

    def boom(_):
        raise RuntimeError("api down")

    summarizer = make_summarizer(analysis_fn=boom)
    result = summarizer.analyze_document_structure("text")
    assert result["status"] == "error"
    assert "api down" in result["analysis"]
