from __future__ import annotations

from dataclasses import dataclass

from .file import File
from .folder import Folder


@dataclass
class Case:
    input: Folder | File
    expected: Folder | File
    id: str
