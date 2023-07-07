from __future__ import annotations

from dataclasses import dataclass

from .file import File


@dataclass
class Case:
    input: File
    expected: File
    id: str
