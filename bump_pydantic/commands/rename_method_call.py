from __future__ import annotations

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst_mypy import MypyTypeInferenceProvider
from rich.pretty import pprint


class RenameMethodCallCommand(VisitorBasedCodemodCommand):
    METADATA_DEPENDENCIES = (MypyTypeInferenceProvider,)

    def __init__(
        self,
        context: CodemodContext,
        classes: tuple[str, ...],
        old_method: str,
        new_method: str,
    ) -> None:
        super().__init__(context)
        self.classes = classes
        self.old_method = old_method
        self.new_method = new_method

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool | None:
        return super().visit_ImportFrom(node)

    def visit_Call(self, node: cst.Call) -> bool | None:
        scope = self.get_metadata(MypyTypeInferenceProvider, node, None)
        if scope is not None:
            pprint(node)
            pprint(scope)
        return super().visit_Call(node)


if __name__ == "__main__":
    import os
    import textwrap
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from libcst.metadata import FullRepoManager

    with TemporaryDirectory() as tmpdir:
        package_dir = f"{tmpdir}/package"
        os.mkdir(package_dir)
        module_path = f"{package_dir}/a.py"
        with open(module_path, "w") as f:
            content = textwrap.dedent(
                """
                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: str

                foo = Foo(bar="text")
                foo.dict()
            """
            )
            f.write(content)
            f.seek(0)
            module = cst.parse_module(content)
        mrg = FullRepoManager(
            package_dir, {module_path}, providers={MypyTypeInferenceProvider}
        )
        wrapper = mrg.get_metadata_wrapper_for_path(module_path)
        context = CodemodContext(wrapper=wrapper)
        command = RenameMethodCallCommand(
            context=context,
            classes=("pydantic.main.BaseModel",),
            old_method="dict",
            new_method="model_dump",
        )
        wrapper.visit(command)
        # for node, mypy_type in mypy_types.items():
        #     pprint((node, mypy_type))
