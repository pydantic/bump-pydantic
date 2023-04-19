from __future__ import annotations

from pathlib import Path

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand


class BaseClassesCollector(VisitorBasedCodemodCommand):
    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.base_classes = {}

    # Visit ClassDef and store name of the class, and location.
    @m.visit(m.ClassDef())
    def visit_class_def(self, node: cst.ClassDef) -> None:
        ...

    @staticmethod
    def collect(files: list[Path]) -> dict[str, list[str]]:
        base_classes = {}
        for file in files:
            with file.open("r") as f:
                mod = cst.parse_module(f.read())
                context = CodemodContext(filename=f.name)
                collector = BaseClassesCollector(context=context)
                mod.visit(visitor=collector)
                base_classes.update(collector.base_classes)
        return base_classes
        return base_classes
