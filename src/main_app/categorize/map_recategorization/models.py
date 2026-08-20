"""Typed values exchanged between the OWID map recategorization layers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MapRecategorization:
    """Normalized metadata and destination categories for one eligible map."""

    region: str
    year: str
    topic: str

    @property
    def location_year_category(self) -> str:
        return f"Category:Our World in Data maps of {self.region} showing {self.year} data"

    @property
    def topic_category(self) -> str:
        return f"Category:Our World in Data maps showing {self.topic}"


@dataclass(frozen=True)
class WikitextRewrite:
    """The planned text replacement for one Commons file page."""

    change: MapRecategorization | None
    text: str
    reason: str | None = None

    @property
    def changed(self) -> bool:
        return self.change is not None


__all__ = ["MapRecategorization", "WikitextRewrite"]
