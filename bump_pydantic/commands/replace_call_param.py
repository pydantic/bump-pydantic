from __future__ import annotations

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand


class ReplaceCallParam(VisitorBasedCodemodCommand):
    def __init__(
        self,
        context: CodemodContext,
        callers: tuple[str, ...],
        old_param: str,
        new_param: str,
    ) -> None:
        super().__init__(context)
        self.callers = callers
        self.old_param = old_param
        self.new_param = new_param
