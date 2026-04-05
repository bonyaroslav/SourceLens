from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".htm", ".html", ".md", ".pdf", ".txt"}


def extract_text_from_path(path: Path) -> str:
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported import file type: {extension}")

    if extension in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    if extension == ".pdf":
        reader = PdfReader(str(path))
        return "\n\n".join(
            page_text.strip()
            for page in reader.pages
            if (page_text := (page.extract_text() or "").strip())
        )

    html = path.read_text(encoding="utf-8", errors="ignore")
    return _extract_html_text(html)


def _extract_html_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
        tag.decompose()

    root = soup.body if soup.body is not None else soup
    lines = [line.strip() for line in root.get_text("\n").splitlines()]
    return "\n".join(line for line in lines if line)
