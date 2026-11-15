"""Generate sample PDFs used by the test suite and manual E2E checks."""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"

SHORT_TEXT = (
    "AI PDF Processor sample document. "
    "This one-page PDF is used to verify text extraction and single-chunk summarisation. "
    "It contains a handful of sentences about invoices, contracts and reports."
)

LONG_PARAGRAPH = (
    "Quarterly operations review. Revenue grew by twelve percent compared with the prior quarter, "
    "driven by strong demand in the enterprise segment. Gross margin held steady at sixty-eight percent. "
    "Customer churn improved to two point one percent after the onboarding redesign shipped in February. "
    "The support team resolved ninety-four percent of tickets within one business day. "
    "Hiring remained on plan, with fourteen engineers joining across three squads. "
    "The board asked for a follow-up plan on international expansion and pricing experiments. "
)


def _write_pdf(path: Path, pages: list[list[str]], title: str = "", author: str = ""):
    c = canvas.Canvas(str(path), pagesize=letter)
    if title:
        c.setTitle(title)
    if author:
        c.setAuthor(author)
    width, height = letter
    for page_lines in pages:
        y = height - 72
        for line in page_lines:
            c.drawString(72, y, line[:110])
            y -= 18
        c.showPage()
    c.save()


def main():
    FIXTURES.mkdir(parents=True, exist_ok=True)

    _write_pdf(
        FIXTURES / "short.pdf",
        [[SHORT_TEXT]],
        title="Short Sample",
        author="AI PDF Processor",
    )

    long_lines = []
    for _ in range(40):
        long_lines.extend([LONG_PARAGRAPH.strip(), ""])
    pages = [long_lines[i:i + 45] for i in range(0, len(long_lines), 45)]
    _write_pdf(
        FIXTURES / "long.pdf",
        pages,
        title="Long Sample",
        author="AI PDF Processor",
    )

    # A PDF with no text layer, simulating a scanned document.
    c = canvas.Canvas(str(FIXTURES / "scanned.pdf"), pagesize=letter)
    c.rect(72, 500, 200, 100, fill=1)
    c.showPage()
    c.save()

    print(f"Fixtures written to {FIXTURES}")


if __name__ == "__main__":
    main()
