"""Line transformation pipeline for logslice."""

import re
from typing import Callable, Iterable, Iterator, List, Optional


TransformFn = Callable[[str], Optional[str]]


def make_strip_transformer() -> TransformFn:
    """Return a transformer that strips leading/trailing whitespace."""
    def transform(line: str) -> Optional[str]:
        return line.strip("\n").strip() + "\n"
    return transform


def make_replace_transformer(pattern: str, replacement: str) -> TransformFn:
    """Return a transformer that replaces regex pattern with replacement."""
    compiled = re.compile(pattern)

    def transform(line: str) -> Optional[str]:
        return compiled.sub(replacement, line)

    return transform


def make_prefix_transformer(prefix: str) -> TransformFn:
    """Return a transformer that prepends a prefix to each line."""
    def transform(line: str) -> Optional[str]:
        stripped = line.rstrip("\n")
        return f"{prefix}{stripped}\n"
    return transform


def make_uppercase_transformer() -> TransformFn:
    """Return a transformer that uppercases each line."""
    def transform(line: str) -> Optional[str]:
        stripped = line.rstrip("\n")
        return stripped.upper() + "\n"
    return transform


def apply_transformers(line: str, transformers: List[TransformFn]) -> Optional[str]:
    """Apply a list of transformers to a line in sequence.

    If any transformer returns None, the line is dropped.
    """
    result: Optional[str] = line
    for fn in transformers:
        if result is None:
            return None
        result = fn(result)
    return result


def transform_lines(
    lines: Iterable[str],
    transformers: List[TransformFn],
) -> Iterator[str]:
    """Apply a pipeline of transformers to an iterable of lines.

    Lines for which any transformer returns None are omitted.
    """
    for line in lines:
        result = apply_transformers(line, transformers)
        if result is not None:
            yield result
