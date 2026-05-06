"""Runner that applies redaction before yielding log lines."""

from typing import Iterable, Iterator, List

from logslice.redactor import redact_lines, resolve_patterns
from logslice.redactor_config import RedactorConfig, validate


def run_with_redaction(
    lines: Iterable[str],
    cfg: RedactorConfig,
) -> Iterator[str]:
    """Yield lines from *lines*, redacting sensitive data when cfg.enabled.

    If redaction is disabled the original lines are passed through unchanged.
    """
    validate(cfg)

    if not cfg.enabled:
        yield from lines
        return

    patterns = resolve_patterns(
        pattern_strings=cfg.custom_patterns,
        builtin_names=cfg.builtin_patterns,
    )

    yield from redact_lines(lines, patterns, mask=cfg.mask)
