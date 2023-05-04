from __future__ import annotations

import libcst as cst
import libcst.matchers as m
from libcst._nodes.statement import AnnAssign, ClassDef
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst_mypy import MypyTypeInferenceProvider
from mypy.nodes import TypeInfo


class AddDefaultNoneCommand(VisitorBasedCodemodCommand):
    """This codemod adds the default value `None` to all fields of a pydantic model that
    are either type `Optional[T]`, `Union[T, None]` or `Any`.

    Example::
        # Before
        from pydantic import BaseModel

        class Foo(BaseModel):
            bar: Optional[str]
            baz: Union[str, None]
            qux: Any

        # After
        from pydantic import BaseModel

        class Foo(BaseModel):
            bar: Optional[str] = None
            baz: Union[str, None] = None
            qux: Any = None
    """

    METADATA_DEPENDENCIES = (MypyTypeInferenceProvider,)

    def __init__(self, context: CodemodContext, class_name: str) -> None:
        super().__init__(context)
        self.class_name = class_name

        self.inside_base_model = False
        self.should_add_none = False

    def visit_ClassDef(self, node: ClassDef) -> None:
        for base in node.bases:
            scope = self.get_metadata(MypyTypeInferenceProvider, base.value, None)
            if scope is not None and isinstance(scope.mypy_type, TypeInfo):
                self.inside_base_model = self._is_class_name_base_of_type_info(
                    self.class_name, scope.mypy_type
                )

    def _is_class_name_base_of_type_info(
        self, class_name: str, type_info: TypeInfo
    ) -> bool:
        if type_info.fullname == class_name:
            return True
        return any(
            self._is_class_name_base_of_type_info(class_name, base.type)
            for base in type_info.bases
        )

    def leave_ClassDef(
        self, original_node: ClassDef, updated_node: ClassDef
    ) -> ClassDef:
        self.inside_base_model = False
        return updated_node

    def visit_AnnAssign(self, node: AnnAssign) -> bool | None:
        if m.matches(
            node.annotation.annotation,
            m.Subscript(
                m.Name("Optional") | m.Attribute(m.Name("typing"), m.Name("Optional"))
            )
            | m.Subscript(
                m.Name("Union") | m.Attribute(m.Name("typing"), m.Name("Union")),
                slice=[
                    m.ZeroOrMore(),
                    m.SubscriptElement(slice=m.Index(m.Name("None"))),
                    m.ZeroOrMore(),
                ],
            )
            | m.Name("Any")
            | m.Attribute(m.Name("typing"), m.Name("Any"))
            # TODO: This can be recursive.
            | m.BinaryOperation(operator=m.BitOr(), left=m.Name("None"))
            | m.BinaryOperation(operator=m.BitOr(), right=m.Name("None")),
        ):
            self.should_add_none = True
        return super().visit_AnnAssign(node)

    def leave_AnnAssign(
        self, original_node: AnnAssign, updated_node: AnnAssign
    ) -> AnnAssign:
        if (
            self.inside_base_model
            and self.should_add_none
            and updated_node.value is None
        ):
            updated_node = updated_node.with_changes(value=cst.Name("None"))
        self.inside_an_assign = False
        self.should_add_none = False
        return updated_node


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
                    bar: Optional[str]
                    baz: Union[str, None]
                    qux: Any
            """
            )
            print(content)
            print("=" * 80)
            f.write(content)
            f.seek(0)
            module = cst.parse_module(content)
        mrg = FullRepoManager(
            package_dir, {module_path}, providers={MypyTypeInferenceProvider}
        )
        wrapper = mrg.get_metadata_wrapper_for_path(module_path)
        context = CodemodContext(wrapper=wrapper)
        command = AddDefaultNoneCommand(
            context=context, class_name="pydantic.main.BaseModel"
        )
        print(wrapper.visit(command).code)
