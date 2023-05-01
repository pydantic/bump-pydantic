from __future__ import annotations

import libcst as cst
import libcst.matchers as m
from libcst._nodes.statement import AnnAssign, ClassDef
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand

# TODO: Support inherited classes from `BaseModel`.

base_model_class = m.ClassDef(
    bases=[
        m.ZeroOrOne(),
        m.Arg(
            value=m.OneOf(
                m.Attribute(value=m.Name("pydantic"), attr=m.Name("BaseModel")),
                m.Name("BaseModel"),
            )
        ),
        m.ZeroOrOne(),
    ]
)
visit_base_model_class = m.visit(base_model_class)
leave_base_model_class = m.leave(base_model_class)


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

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.inside_base_model = False

    @visit_base_model_class
    def visit_base_model(self, _: ClassDef) -> None:
        self.inside_base_model = True

    @leave_base_model_class
    def leave_base_model(self, _: ClassDef, updated_node: ClassDef) -> ClassDef:
        self.inside_base_model = False
        return updated_node

    def leave_AnnAssign(
        self, original_node: AnnAssign, updated_node: AnnAssign
    ) -> AnnAssign:
        if self.inside_base_model and updated_node.value is None:
            updated_node = updated_node.with_changes(value=cst.Name("None"))
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
        mrg = FullRepoManager(package_dir, {module_path}, providers={})
        wrapper = mrg.get_metadata_wrapper_for_path(module_path)
        context = CodemodContext(wrapper=wrapper)
        command = AddDefaultNoneCommand(context=context)
        print(wrapper.visit(command).code)
