import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_document(file_path: str) -> str:
    """Extract plain text from a PDF, DOCX, or TXT file."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    loaders = {
        ".txt": _load_txt,
        ".pdf": _load_pdf,
        ".docx": _load_docx,
    }

    loader = loaders.get(suffix)
    if loader is None:
        raise ValueError(f"Unsupported file format: {suffix}")

    text = loader(path)
    logger.info("Loaded %s (%d chars)", path.name, len(text))
    return text


# ---------------------------------------------------------------------------
# Format-specific loaders
# ---------------------------------------------------------------------------

def _load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError(
            "pypdf is required for PDF support. Install with: pip install pypdf"
        ) from exc

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def _load_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise ImportError(
            "python-docx is required for DOCX support. Install with: pip install python-docx"
        ) from exc

    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """Split *text* into overlapping chunks, preferring sentence boundaries."""
    if not text.strip():
        return []
    return _recursive_split(text, ["\n\n", "\n", ". ", "! ", "? ", " "], chunk_size, chunk_overlap)


def _recursive_split(
    text: str,
    separators: list[str],
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    if len(text) <= chunk_size:
        return [text.strip()] if text.strip() else []

    sep = separators[0] if separators else ""
    remaining_seps = separators[1:] if len(separators) > 1 else [""]

    if sep:
        parts = text.split(sep)
    else:
        parts = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)]

    chunks: list[str] = []
    current = ""

    for part in parts:
        candidate = f"{current}{sep}{part}" if current else part

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current.strip():
                chunks.append(current.strip())

            if len(part) > chunk_size and remaining_seps:
                chunks.extend(_recursive_split(part, remaining_seps, chunk_size, chunk_overlap))
                current = ""
            else:
                overlap_text = current[-chunk_overlap:] if chunk_overlap and current else ""
                current = f"{overlap_text}{sep}{part}" if overlap_text else part

    if current.strip():
        chunks.append(current.strip())

    return chunks
