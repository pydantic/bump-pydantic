from __future__ import annotations

from collections import defaultdict

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.metadata import FullyQualifiedNameProvider, QualifiedName


class ClassDefVisitor(VisitorBasedCodemodCommand):
    METADATA_DEPENDENCIES = {FullyQualifiedNameProvider}

    CONTEXT_KEY = "class_def_visitor"

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.module_fqn: None | QualifiedName = None
        self.context.scratch.setdefault(self.CONTEXT_KEY, defaultdict(set))

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        fqn_set = self.get_metadata(FullyQualifiedNameProvider, node)

        if not fqn_set:
            return None

        fqn: QualifiedName = next(iter(fqn_set))  # type: ignore
        for arg in node.bases:
            base_fqn_set = self.get_metadata(FullyQualifiedNameProvider, arg.value)

            if not base_fqn_set:
                return None

            base_fqn: QualifiedName = next(iter(base_fqn_set))  # type: ignore
            # NOTE: Should I use the name or the QualifiedName?
            self.context.scratch[self.CONTEXT_KEY][fqn.name].add(base_fqn.name)


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
        pprint(context.scratch[ClassDefVisitor.CONTEXT_KEY])
