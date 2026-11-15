import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    path = ROOT / "tests" / "fixtures"
    if not (path / "short.pdf").exists():
        from scripts.make_fixtures import main as make_fixtures

        make_fixtures()
    return path
