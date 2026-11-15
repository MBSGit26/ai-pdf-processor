from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def test_app_renders_without_exceptions():
    at = AppTest.from_file(str(ROOT / "app.py"))
    at.run(timeout=60)

    assert not at.exception
    assert at.title[0].value.startswith("📄")
