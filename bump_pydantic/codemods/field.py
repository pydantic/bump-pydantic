from typing import List, Union

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor, RemoveImportsVisitor

RENAMED_KEYWORDS = {
    "min_items": "min_length",
    "max_items": "max_length",
    "allow_mutation": "frozen",
    "example": "examples",
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

ANN_ASSIGN_WITH_FIELD = m.AnnAssign(
    value=m.Call(func=m.Name("Field")),
) | m.AnnAssign(
    annotation=m.Annotation(
        annotation=m.Subscript(
            slice=[
                m.ZeroOrMore(),
                m.SubscriptElement(slice=m.Index(value=m.Call(func=m.Name("Field")))),
                m.ZeroOrMore(),
            ]
        )
    )
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

    @m.visit(ANN_ASSIGN_WITH_FIELD)
    def visit_field_assign(self, node: cst.AnnAssign) -> None:
        self.inside_field_assign = True
        self._const: Union[cst.Arg, None] = None

    @m.leave(ANN_ASSIGN_WITH_FIELD)
    def leave_field_assign(self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign) -> cst.AnnAssign:
        self.inside_field_assign = False

        if self._const is None:
            return updated_node

        AddImportsVisitor.add_needed_import(self.context, "typing", "Literal")
        RemoveImportsVisitor.remove_unused_import(self.context, "pydantic", "Field")
        return updated_node.with_changes(
            annotation=cst.Annotation(
                annotation=cst.Subscript(
                    value=cst.Name("Literal"),
                    slice=[cst.SubscriptElement(slice=cst.Index(value=self._const.value))],
                )
            ),
            value=self._const.value,
        )

    @m.visit(m.Call(func=m.Name("Field")))
    def visit_field_call(self, node: cst.Call) -> None:
        # Check if there's a `const=True` argument.
        const_arg = m.Arg(value=m.Name("True"), keyword=m.Name("const"))
        if m.matches(node, m.Call(func=m.Name("Field"), args=[~m.Arg(value=m.Name("...")), const_arg])):
            self._const = node.args[0]

    @m.leave(m.Call(func=m.Name("Field")))
    def leave_field_call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        if not self.has_field_import or not self.inside_field_assign:
            return updated_node

        new_args: List[cst.Arg] = []
        for arg in updated_node.args:
            if m.matches(arg, m.Arg(keyword=m.Name())):
                keyword = RENAMED_KEYWORDS.get(arg.keyword.value, arg.keyword.value)  # type: ignore
                value = arg.value
                if arg.keyword:
                    if arg.keyword.value == "allow_mutation":
                        # The `allow_mutation` keyword is the negative of `frozen`.
                        if m.matches(arg.value, m.Name(value="False")):
                            value = cst.Name("True")
                        elif m.matches(arg.value, m.Name(value="True")):
                            value = cst.Name("False")
                    if arg.keyword.value == "example":
                        # The example keyword is now a list, `examples`.
                        value = cst.List([cst.Element(arg.value)])
                new_arg = arg.with_changes(keyword=arg.keyword.with_changes(value=keyword), value=value)  # type: ignore
                new_args.append(new_arg)  # type: ignore
            else:
                new_args.append(arg)

        return updated_node.with_changes(args=new_args)


if __name__ == "__main__":
    import textwrap

    from rich.console import Console

    console = Console()

    source = textwrap.dedent(
        """
        from typing import Annotated

        from pydantic import BaseModel, Field

        class A(BaseModel):
            a: Annotated[List[str], Field(..., description="My description", min_items=1)]
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
