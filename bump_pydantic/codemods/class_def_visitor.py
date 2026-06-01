"""
There are two objects in the visitor:
1. `base_model_cls` (Set[str]): Set of classes that are BaseModel based.
2. `cls` (Dict[str, Set[str]]): A dictionary mapping each class definition to a set of base classes.

`base_model_cls` accumulates on each iteration.
`cls` also accumulates on each iteration, but it's also partially solved:
1. Check if the module visited is a prefix of any `cls.keys()`.
1.1. If it is, and if any `base_model_cls` is found, remove from `cls`, and add to `base_model_cls`.
1.2. If it's not, it continues on the `cls`
"""

from __future__ import annotations

from collections import defaultdict
from typing import Set, cast

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.metadata import FullyQualifiedNameProvider, QualifiedName


class ClassDefVisitor(VisitorBasedCodemodCommand):
    METADATA_DEPENDENCIES = {FullyQualifiedNameProvider}

    BASE_MODEL_CONTEXT_KEY = "base_model_cls"
    NO_BASE_MODEL_CONTEXT_KEY = "no_base_model_cls"
    CLS_CONTEXT_KEY = "cls"

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.module_fqn: None | QualifiedName = None

        self.context.scratch.setdefault(
            self.BASE_MODEL_CONTEXT_KEY,
            {"pydantic.BaseModel", "pydantic.main.BaseModel"},
        )
        self.context.scratch.setdefault(self.NO_BASE_MODEL_CONTEXT_KEY, set())
        self.context.scratch.setdefault(self.CLS_CONTEXT_KEY, defaultdict(set))

    def _recursively_disambiguate(self, classname: str, context_set: set[str]) -> None:
        if classname in context_set and classname in self.context.scratch[self.CLS_CONTEXT_KEY]:
            for child_classname in self.context.scratch[self.CLS_CONTEXT_KEY].pop(classname):
                context_set.add(child_classname)
                self._recursively_disambiguate(child_classname, context_set)

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        fqn_set = self.get_metadata(FullyQualifiedNameProvider, node)

        if not fqn_set:
            return None

        fqn: QualifiedName = next(iter(fqn_set))  # type: ignore

        if not node.bases:
            self.context.scratch[self.NO_BASE_MODEL_CONTEXT_KEY].add(fqn.name)

        for arg in node.bases:
            base_fqn_set = self.get_metadata(FullyQualifiedNameProvider, arg.value)
            base_fqn_set = base_fqn_set or set()

            for base_fqn in cast(Set[QualifiedName], iter(base_fqn_set)):  # type: ignore
                if base_fqn.name in self.context.scratch[self.BASE_MODEL_CONTEXT_KEY]:
                    self.context.scratch[self.BASE_MODEL_CONTEXT_KEY].add(fqn.name)
                elif base_fqn.name in self.context.scratch[self.NO_BASE_MODEL_CONTEXT_KEY]:
                    self.context.scratch[self.NO_BASE_MODEL_CONTEXT_KEY].add(fqn.name)

            # In case we have the following scenario:
            # class ChildA(A):
            # class A(B): ...
            # class B(BaseModel): ...
            # class D(C): ...
            # class C: ...
            # We want to disambiguate `A` and then `ChildA` as soon as we see `B` is a `BaseModel`.
            # We recursively add child classes to self.BASE_MODEL_CONTEXT_KEY.
            self._recursively_disambiguate(fqn.name, self.context.scratch[self.BASE_MODEL_CONTEXT_KEY])

            # In case we have the following scenario:
            # class A(B): ...
            # class B(BaseModel): ...
            # class E(D): ...
            # class D(C): ...
            # class C: ...
            # We want to disambiguate `D` and then `E` as soon as we see `C` is NOT a `BaseModel`.
            # We recursively add child classes to self.NO_BASE_MODEL_CONTEXT_KEY.
            self._recursively_disambiguate(fqn.name, self.context.scratch[self.NO_BASE_MODEL_CONTEXT_KEY])

            # In case we have the following scenario:
            # class A(B): ...
            # ...And B is not known.
            # We want to make sure that B -> A is added to the `cls` context, so if we find B later,
            # we can disambiguate.
            if fqn.name not in (
                *self.context.scratch[self.BASE_MODEL_CONTEXT_KEY],
                *self.context.scratch[self.NO_BASE_MODEL_CONTEXT_KEY],
            ):
                for base_fqn in cast(Set[QualifiedName], base_fqn_set):
                    self.context.scratch[self.CLS_CONTEXT_KEY][base_fqn.name].add(fqn.name)

    # TODO: Implement this if needed...
    def next_file(self, visited: set[str]) -> str | None:
        return None


if __name__ == "__main__":
    import os
    import textwrap
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from libcst.metadata import FullRepoManager
    from rich.pretty import pprint

    with TemporaryDirectory(dir=os.getcwd()) as tmpdir:
        package_dir = f"{tmpdir}/package"
        os.mkdir(package_dir)
        module_path = f"{package_dir}/a.py"
        with open(module_path, "w") as f:
            content = textwrap.dedent(
                """
                from pydantic import BaseModel

                class Foo(BaseModel):
                    a: str

                class Bar(Foo):
                    b: str

                class Potato:
                    ...

                class Spam(Potato):
                    ...

                foo = Foo(a="text")
                foo.dict()
            """
            )
            f.write(content)
        module = str(Path(module_path).relative_to(tmpdir))
        mrg = FullRepoManager(tmpdir, {module}, providers={FullyQualifiedNameProvider})
        wrapper = mrg.get_metadata_wrapper_for_path(module)
        context = CodemodContext(wrapper=wrapper)
        command = ClassDefVisitor(context=context)
        mod = wrapper.visit(command)
        pprint(context.scratch[ClassDefVisitor.BASE_MODEL_CONTEXT_KEY])
        pprint(context.scratch[ClassDefVisitor.NO_BASE_MODEL_CONTEXT_KEY])
        pprint(context.scratch[ClassDefVisitor.CLS_CONTEXT_KEY])
