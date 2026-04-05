from dataclasses import dataclass

TARGET_CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    chunk_index: int
    text: str


def chunk_text(
    text: str,
    *,
    source_id: str = "source",
    target_size: int = TARGET_CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[TextChunk]:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    if not paragraphs:
        return []

    chunk_texts: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= target_size:
            current = candidate
            continue

        if current:
            chunk_texts.append(current)
            current = _with_overlap(current, paragraph, overlap=overlap)
            if len(current) <= target_size:
                continue

        split_parts = _hard_split(paragraph, target_size=target_size, overlap=overlap)
        if split_parts:
            chunk_texts.extend(split_parts[:-1])
            current = split_parts[-1]
        else:
            current = paragraph

    if current:
        chunk_texts.append(current)

    return [
        TextChunk(
            chunk_id=f"{source_id}:{index}",
            chunk_index=index,
            text=chunk,
        )
        for index, chunk in enumerate(chunk_texts)
    ]


def _with_overlap(previous_chunk: str, next_paragraph: str, *, overlap: int) -> str:
    overlap_text = previous_chunk[-overlap:].strip()
    if not overlap_text:
        return next_paragraph
    return f"{overlap_text}\n\n{next_paragraph}"


def _hard_split(text: str, *, target_size: int, overlap: int) -> list[str]:
    segments: list[str] = []
    remaining = text.strip()
    while len(remaining) > target_size:
        split_at = remaining.rfind(" ", 0, target_size)
        if split_at <= 0:
            split_at = target_size
        segment = remaining[:split_at].strip()
        if not segment:
            break
        segments.append(segment)
        start = max(0, split_at - overlap)
        remaining = remaining[start:].strip()
    if remaining:
        segments.append(remaining)
    return segments
