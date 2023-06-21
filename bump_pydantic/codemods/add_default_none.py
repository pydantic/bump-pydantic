from __future__ import annotations

import libcst as cst
import libcst.matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.metadata import FullyQualifiedNameProvider, QualifiedName

from bump_pydantic.codemods.class_def_visitor import ClassDefVisitor
from bump_pydantic.markers.find_base_model import CONTEXT_KEY as BASE_MODEL_CONTEXT_KEY
from bump_pydantic.markers.find_base_model import find_base_model


class AddDefaultNoneCommand(VisitorBasedCodemodCommand):
    """This codemod adds the default value `None` to all fields of a pydantic model that
    are either type `Optional[T]`, `Union[T, None]` or `Any`.

    Example::
        # Before
        ```py
        from pydantic import BaseModel

        class Foo(BaseModel):
            bar: Optional[str]
            baz: Union[str, None]
            qux: Any
        ```

        # After
        ```py
        from pydantic import BaseModel

        class Foo(BaseModel):
            bar: Optional[str] = None
            baz: Union[str, None] = None
            qux: Any = None
        ```
    """

    METADATA_DEPENDENCIES = (FullyQualifiedNameProvider,)

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)

        self.inside_base_model = False
        self.should_add_none = False

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        fqn_set = self.get_metadata(FullyQualifiedNameProvider, node)

        if not fqn_set:
            return None

        fqn: QualifiedName = next(iter(fqn_set))  # type: ignore
        if fqn.name in self.context.scratch[BASE_MODEL_CONTEXT_KEY]:
            self.inside_base_model = True

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        self.inside_base_model = False
        return updated_node

    def visit_AnnAssign(self, node: cst.AnnAssign) -> bool | None:
        if m.matches(
            node.annotation.annotation,
            m.Subscript(m.Name("Optional") | m.Attribute(m.Name("typing"), m.Name("Optional")))
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
            # TODO: This can be recursive. Can it?
            | m.BinaryOperation(operator=m.BitOr(), left=m.Name("None"))
            | m.BinaryOperation(operator=m.BitOr(), right=m.Name("None")),
        ):
            self.should_add_none = True
        return super().visit_AnnAssign(node)

    def leave_AnnAssign(self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign) -> cst.AnnAssign:
        if self.inside_base_model and self.should_add_none and updated_node.value is None:
            updated_node = updated_node.with_changes(value=cst.Name("None"))
        self.inside_an_assign = False
        self.should_add_none = False
        return updated_node


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
                    a: Optional[str]

                class Bar(Foo):
                    b: Optional[str]
                    c: Union[str, None]
                    d: Any

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
        pprint(context.scratch)

        command = AddDefaultNoneCommand(context=context)  # type: ignore[assignment]
        mod = wrapper.visit(command)
        print(mod.code)
