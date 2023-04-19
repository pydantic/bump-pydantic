from __future__ import annotations

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand


class RenameMethodCommand(VisitorBasedCodemodCommand):
    def __init__(
        self,
        context: CodemodContext,
        base_classes: tuple[str, ...],
        old_method: str,
        new_method: str,
    ) -> None:
        super().__init__(context)
        self.base_classes = base_classes
        self.old_method = old_method
        self.new_method = new_method
