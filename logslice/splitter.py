"""Log file splitter: splits filtered lines into chunks by count or size."""

from typing import Iterator, List


def split_by_count(lines: List[str], chunk_size: int) -> Iterator[List[str]]:
    """Yield successive chunks of up to chunk_size lines."""
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    for i in range(0, len(lines), chunk_size):
        yield lines[i : i + chunk_size]


def split_by_size(lines: List[str], max_bytes: int) -> Iterator[List[str]]:
    """Yield chunks of lines whose total byte size does not exceed max_bytes."""
    if max_bytes <= 0:
        raise ValueError(f"max_bytes must be positive, got {max_bytes}")
    current: List[str] = []
    current_size = 0
    for line in lines:
        line_size = len(line.encode("utf-8"))
        if current and current_size + line_size > max_bytes:
            yield current
            current = []
            current_size = 0
        current.append(line)
        current_size += line_size
    if current:
        yield current


def split_lines(
    lines: List[str],
    chunk_size: int = None,
    max_bytes: int = None,
) -> Iterator[List[str]]:
    """Split lines by count or size. Exactly one strategy must be specified."""
    if chunk_size is not None and max_bytes is not None:
        raise ValueError("Specify either chunk_size or max_bytes, not both.")
    if chunk_size is not None:
        return split_by_count(lines, chunk_size)
    if max_bytes is not None:
        return split_by_size(lines, max_bytes)
    raise ValueError("Either chunk_size or max_bytes must be specified.")
