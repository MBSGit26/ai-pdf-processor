from utils import (
    create_summary_dataframe,
    estimate_processing_time,
    export_summary_to_text,
)


SAMPLE = {
    "summary_type": "bullet_points",
    "total_chunks": 2,
    "combined_summary": "Final combined text.",
    "individual_summaries": [
        {"chunk_number": 1, "summary": "first", "ok": True, "original_length": 100, "summary_length": 50},
        {"chunk_number": 2, "summary": "second", "ok": True, "original_length": 80, "summary_length": 40},
    ],
}


def test_export_summary_contains_header_and_sections():
    text = export_summary_to_text(SAMPLE, "report.pdf")
    assert "File: report.pdf" in text
    assert "Summary Type: Bullet Points" in text
    assert "Final combined text." in text
    assert "Chunk 1:" in text and "Chunk 2:" in text


def test_dataframe_has_one_row_per_chunk():
    df = create_summary_dataframe(SAMPLE)
    assert len(df) == 2
    assert list(df.columns) == [
        "Chunk", "Original Length", "Summary Length", "Compression Ratio", "Status",
    ]
    assert df.loc[0, "Compression Ratio"] == 0.5
    assert set(df["Status"]) == {"Success"}


def test_estimate_processing_time_scales_with_chunks():
    assert estimate_processing_time(1).startswith("~")
    assert "min" in estimate_processing_time(200)
