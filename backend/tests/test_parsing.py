from pathlib import Path

from source_lens_api.ingest.chunking import chunk_text
from source_lens_api.ingest.parsing import extract_text_from_path
from source_lens_api.ingest.text import normalize_text

from .support import write_minimal_pdf, write_text_fixture


def test_extract_text_from_txt_file(tmp_path: Path) -> None:
    path = write_text_fixture(tmp_path / "sample.txt", "Alpha\r\n\r\nBeta")

    text = extract_text_from_path(path)

    assert normalize_text(text) == "Alpha\n\nBeta"


def test_extract_text_from_markdown_file(tmp_path: Path) -> None:
    path = write_text_fixture(tmp_path / "sample.md", "# Title\n\n- item")

    text = extract_text_from_path(path)

    assert "Title" in text


def test_extract_text_from_pdf_file(tmp_path: Path) -> None:
    path = write_minimal_pdf(tmp_path / "sample.pdf", "Hello PDF")

    text = extract_text_from_path(path)

    assert "Hello PDF" in normalize_text(text)


def test_extract_text_from_html_file_removes_navigation_noise(tmp_path: Path) -> None:
    path = write_text_fixture(
        tmp_path / "sample.html",
        """
        <html>
          <body>
            <nav>Ignore this nav</nav>
            <h1>Real title</h1>
            <p>Important body text.</p>
            <script>const hidden = true;</script>
          </body>
        </html>
        """,
    )

    text = extract_text_from_path(path)

    assert "Real title" in text
    assert "Important body text." in text
    assert "Ignore this nav" not in text


def test_extract_text_from_htm_file(tmp_path: Path) -> None:
    path = write_text_fixture(tmp_path / "sample.htm", "<body><p>HTML short form</p></body>")

    text = extract_text_from_path(path)

    assert "HTML short form" in text


def test_chunk_text_splits_long_paragraphs_with_overlap(tmp_path: Path) -> None:
    del tmp_path
    text = normalize_text(("paragraph " * 220).strip())

    chunks = chunk_text(text, source_id="source-1", target_size=200, overlap=30)

    assert len(chunks) > 1
    assert chunks[0].chunk_id == "source-1:0"
    assert all(chunk.text for chunk in chunks)
