from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.metadata import ImportAssignment, ScopeProvider
from rich.pretty import pprint


class BaseClassesCollector(VisitorBasedCodemodCommand):
    METADATA_DEPENDENCIES = (ScopeProvider,)

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.base_classes = defaultdict(list)
        self.module_name = extract_module_name(
            context.filename, context.full_package_name
        )
        self.import_assignments: list[ImportAssignment] = []

    def visit_Module(self, node: cst.Module) -> None:
        scope = self.get_metadata(ScopeProvider, node)
        if scope is not None:
            for assignment in scope.assignments:
                if isinstance(assignment, ImportAssignment):
                    self.import_assignments.append(assignment)

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        for assignment in self.import_assignments:
            for base_class in node.bases:
                name = base_class.value
                if m.matches(name, m.Name()):
                    full_path = self.module_name + "." + node.name.value
                    qualified_names = assignment.get_qualified_names_for(name.value)
                    self.base_classes[full_path].extend(qualified_names)

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


def extract_module_name(filename: str | None, package: str | None) -> str:
    if filename is None or package is None:
        raise AssertionError("filename and package must be provided")
    splitted_path = filename.split("/")
    index = splitted_path.index(package)
    return ".".join(splitted_path[index:])
