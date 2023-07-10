from __future__ import annotations

import sys
from argparse import ArgumentParser

from mypy.build import build
from mypy.main import process_options
from mypy.nodes import ClassDef
from mypy.traverser import TraverserVisitor

CONTEXT_KEY = "mypy_visitor"


class MyPyVisitor(TraverserVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.classes: dict[str, bool] = {}

    def visit_class_def(self, o: ClassDef) -> None:
        super().visit_class_def(o)
        self.classes[o.fullname] = o.info.has_base("pydantic.main.BaseModel")


def run_mypy_visitor(arg_files: list[str]) -> dict[str, bool]:
    files, opt = process_options(arg_files, stdout=sys.stdout, stderr=sys.stderr)

    opt.export_types = True
    opt.incremental = True
    opt.fine_grained_incremental = True
    opt.cache_fine_grained = True
    opt.allow_redefinition = True
    opt.local_partial_types = True

    result = build(files, opt, stdout=sys.stdout, stderr=sys.stderr)

    visitor = MyPyVisitor()
    classes: dict[str, bool] = {}

    for file in files:
        tree = result.graph[file.module].tree
        if tree:
            tree.accept(visitor=visitor)
            classes.update(visitor.classes)
    return classes


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    run_mypy_visitor(args.files)
