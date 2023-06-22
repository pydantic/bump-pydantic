from typing import List

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor

RENAMED_KEYWORDS = {
    "min_items": "min_length",
    "max_items": "max_length",
    "allow_mutation": "frozen",
    "regex": "pattern",
    # NOTE: This is only for BaseSettings.
    "env": "validation_alias",
}

IMPORT_FIELD = m.Module(
    body=[
        m.ZeroOrMore(),
        m.SimpleStatementLine(
            body=[
                m.ZeroOrMore(),
                m.ImportFrom(
                    module=m.Name("pydantic"),
                    names=[
                        m.ZeroOrMore(),
                        m.ImportAlias(name=m.Name("Field")),
                        m.ZeroOrMore(),
                    ],
                )
                | m.ImportFrom(
                    module=m.Name("pydantic") | m.Name("pydantic_settings"),
                    names=[
                        m.ZeroOrMore(),
                        m.ImportAlias(name=m.Name("BaseSettings")),
                        m.ZeroOrMore(),
                    ],
                ),
                m.ZeroOrMore(),
            ],
        ),
        m.ZeroOrMore(),
    ]
)


class FieldCodemod(VisitorBasedCodemodCommand):
    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)

        self.has_field_import = False
        self.inside_field_assign = False

    @m.visit(IMPORT_FIELD)
    def visit_field_import(self, node: cst.Module) -> None:
        self.has_field_import = True

    @m.leave(IMPORT_FIELD)
    def leave_field_import(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        self.has_field_import = False
        return updated_node

    @m.visit(m.AnnAssign(value=m.Call(func=m.Name("Field"))))
    def visit_field_assign(self, node: cst.AnnAssign) -> None:
        self.inside_field_assign = True

    @m.leave(m.AnnAssign(value=m.Call(func=m.Name("Field"))))
    def leave_field_assign(self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign) -> cst.AnnAssign:
        self.inside_field_assign = False
        return updated_node

    @m.leave(m.Call(func=m.Name("Field")))
    def leave_field_call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        if not self.has_field_import or not self.inside_field_assign:
            return updated_node

        new_args: List[cst.Arg] = []
        for arg in updated_node.args:
            if m.matches(arg, m.Arg(keyword=m.Name())):
                keyword = RENAMED_KEYWORDS.get(arg.keyword.value, arg.keyword.value)  # type: ignore
                new_args.append(arg.with_changes(keyword=arg.keyword.with_changes(value=keyword)))  # type: ignore
            else:
                new_args.append(arg)

        return updated_node.with_changes(args=new_args)


if __name__ == "__main__":
    import textwrap

    from rich.console import Console

    console = Console()

    source = textwrap.dedent(
        """
        from pydantic import BaseModel, Field

        class A(BaseModel):
            a: List[str] = Field(..., description="My description", min_items=1)
        """
    )
    console.print(source)
    console.print("=" * 80)

    mod = cst.parse_module(source)
    context = CodemodContext(filename="main.py")
    wrapper = cst.MetadataWrapper(mod)
    command = FieldCodemod(context=context)
    console.print(mod)

    mod = wrapper.visit(command)
    wrapper = cst.MetadataWrapper(mod)
    command = AddImportsVisitor(context=context)  # type: ignore[assignment]
    mod = wrapper.visit(command)
    console.print(mod.code)
