from __future__ import annotations

from collections import defaultdict
from typing import Any

from libcst.codemod import CodemodContext

from bump_pydantic.codemods.class_def_visitor import ClassDefVisitor

CONTEXT_KEY = "find_base_model"


def revert_dictionary(classes: defaultdict[str, set[str]]) -> defaultdict[str, set[str]]:
    revert_classes: defaultdict[str, set[str]] = defaultdict(set)
    for cls, bases in classes.copy().items():
        for base in bases:
            revert_classes[base].add(cls)
    return revert_classes


def find_base_model(scratch: dict[str, Any]) -> None:
    classes = scratch[ClassDefVisitor.CONTEXT_KEY]
    revert_classes = revert_dictionary(classes)
    base_model_set: set[str] = set()

    for cls, bases in revert_classes.copy().items():
        if cls in ("pydantic.BaseModel", "BaseModel"):
            base_model_set = base_model_set.union(bases)

            visited: set[str] = set()
            bases_queue = list(bases)
            while bases_queue:
                base = bases_queue.pop()

                if base in visited:
                    continue
                visited.add(base)

                base_model_set.add(base)
                bases_queue.extend(revert_classes[base])

    scratch[CONTEXT_KEY] = base_model_set


if __name__ == "__main__":
    import os
    import textwrap
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from libcst.metadata import FullRepoManager, FullyQualifiedNameProvider
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
        find_base_model(scratch=context.scratch)
        pprint(context.scratch[CONTEXT_KEY])
