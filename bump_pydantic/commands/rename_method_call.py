from __future__ import annotations

import libcst as cst
from typing import cast
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst_mypy import MypyTypeInferenceProvider
from mypy.nodes import TypeInfo
from mypy.types import Instance


class RenameMethodCallCommand(VisitorBasedCodemodCommand):
    """This codemod renames a method call of a class.

    Example::
        # Given the following class and method mapping:
        # class_name = "pydantic.main.BaseModel"
        # methods = {"dict": "model_dump"}

        # Before

        from pydantic import BaseModel

        class Foo(BaseModel):
            bar: str

        foo = Foo(bar="text")
        foo.dict()

        # After

        from pydantic import BaseModel

        class Foo(BaseModel):
            bar: str

        foo = Foo(bar="text")
        foo.model_dump()
    """

    METADATA_DEPENDENCIES = (MypyTypeInferenceProvider,)

    def __init__(
        self,
        context: CodemodContext,
        class_name: str,
        methods: dict[str, str],
    ) -> None:
        super().__init__(context)
        self.class_name = class_name
        self.methods = methods

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        node = original_node
        if m.matches(node.func, m.Attribute()):
            func = cst.ensure_type(node.func, cst.Attribute)
            scope = self.get_metadata(MypyTypeInferenceProvider, func.value, None)
            if scope is not None:
                mypy_type = scope.mypy_type
                if isinstance(mypy_type, Instance):
                    info = mypy_type.type
                    if self._is_class_name_base_of_type_info(self.class_name, info):
                        new_method = self.methods.get(func.attr.value)
                        if new_method is not None:
                            attr = func.attr.with_changes(value=new_method)
                            func_with_changes = func.with_changes(attr=attr)
                            return updated_node.with_changes(func=func_with_changes)
        return updated_node

    def _is_class_name_base_of_type_info(
        self, class_name: str, type_info: TypeInfo
    ) -> bool:
        if type_info.fullname == class_name:
            return True
        return any(
            self._is_class_name_base_of_type_info(class_name, base.type)
            for base in type_info.bases
        )


if __name__ == "__main__":
    import os
    import textwrap
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
        mrg = FullRepoManager(
            package_dir, {module_path}, providers={MypyTypeInferenceProvider}
        )
        wrapper = mrg.get_metadata_wrapper_for_path(module_path)
        context = CodemodContext(wrapper=wrapper)
        command = RenameMethodCallCommand(
            context=context,
            class_name="pydantic.main.BaseModel",
            methods={"dict": "model_dump"},
        )
        print(wrapper.visit(command).code)
