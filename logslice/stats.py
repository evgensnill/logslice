"""Statistics collection and reporting for log parsing runs."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ParseStats:
    total_lines: int = 0
    matched_lines: int = 0
    skipped_lines: int = 0
    error_lines: int = 0
    pattern_hits: Dict[str, int] = field(default_factory=dict)

    def record_match(self, pattern: Optional[str] = None) -> None:
        self.matched_lines += 1
        if pattern:
            self.pattern_hits[pattern] = self.pattern_hits.get(pattern, 0) + 1

    def record_skip(self) -> None:
        self.skipped_lines += 1

    def record_error(self) -> None:
        self.error_lines += 1

    def record_line(self) -> None:
        self.total_lines += 1

    @property
    def match_rate(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return self.matched_lines / self.total_lines

    def to_dict(self) -> Dict:
        return {
            "total_lines": self.total_lines,
            "matched_lines": self.matched_lines,
            "skipped_lines": self.skipped_lines,
            "error_lines": self.error_lines,
            "match_rate": round(self.match_rate, 4),
            "pattern_hits": dict(self.pattern_hits),
        }

    def summary(self) -> str:
        return (
            f"Lines: {self.total_lines} total, "
            f"{self.matched_lines} matched "
            f"({self.match_rate:.1%}), "
            f"{self.skipped_lines} skipped, "
            f"{self.error_lines} errors"
        )
