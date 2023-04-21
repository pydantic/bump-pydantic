from __future__ import annotations

import os

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.metadata import TypeInferenceProvider
from rich.pretty import pprint


class RenameMethodCallCommand(VisitorBasedCodemodCommand):
    METADATA_DEPENDENCIES = (TypeInferenceProvider,)

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
        scope = self.get_metadata(TypeInferenceProvider, node)
        if scope is not None:
            pprint(scope)
        return super().visit_Call(node)


if __name__ == "__main__":
    import textwrap
    from tempfile import TemporaryDirectory

    from libcst.metadata import FullRepoManager

    with TemporaryDirectory() as tmpdir:
        package_dir = f"{tmpdir}/package"
        os.mkdir(package_dir)
        module_path = f"{package_dir}/a.py"
        with open(module_path, "w") as f:
            f.write(
                textwrap.dedent(
                    """
                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: str

                foo = Foo(bar="text")
                foo.dict()
            """
                )
            )
        mgr = FullRepoManager(tmpdir, {module_path}, {TypeInferenceProvider})
        wrapper = mgr.get_metadata_wrapper_for_path(module_path)

        context = CodemodContext()
        command = RenameMethodCallCommand(
            context=context,
            classes=("pydantic.BaseModel",),
            old_method="dict",
            new_method="model_dump",
        )
        module = wrapper.visit(command)
        pprint(module)
