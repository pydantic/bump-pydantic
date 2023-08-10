from typing import List

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor

PREFIX_COMMENT = "# TODO[pydantic]: "
REFACTOR_COMMENT = f"{PREFIX_COMMENT}We couldn't refactor `{{old_name}}`, please create the `{{new_name}}` manually."
GET_VALIDATORS_COMMENT = REFACTOR_COMMENT.format(old_name="__get_validators__", new_name="__get_pydantic_core_schema__")
MODIFY_SCHEMA_COMMENT = REFACTOR_COMMENT.format(old_name="__modify_schema__", new_name="__get_pydantic_json_schema__")
CHECK_LINK_COMMENT = "# Check https://docs.pydantic.dev/latest/migration/#defining-custom-types for more information."

GET_VALIDATORS_FUNCTION = m.FunctionDef(name=m.Name("__get_validators__"))
MODIFY_SCHEMA_FUNCTION = m.FunctionDef(name=m.Name("__modify_schema__"))


class CustomTypeCodemod(VisitorBasedCodemodCommand):
    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)

        self._already_modified = False
        self._should_add_comment = False
        self._has_comment = False
        self._args: List[cst.Arg] = []

    @m.visit(GET_VALIDATORS_FUNCTION)
    def visit_get_validators_func(self, node: cst.FunctionDef) -> None:
        for line in node.leading_lines:
            if m.matches(line, m.EmptyLine(comment=m.Comment(value=CHECK_LINK_COMMENT))):
                self._has_comment = True

    @m.leave(MODIFY_SCHEMA_FUNCTION)
    def leave_modify_schema_func(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        if self._has_comment:
            self._has_comment = False
            return updated_node

        return self._function_with_leading_comment_after_optional_decorators(updated_node, MODIFY_SCHEMA_COMMENT)

    @m.leave(GET_VALIDATORS_FUNCTION)
    def leave_get_validators_func(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        if self._has_comment:
            self._has_comment = False
            return updated_node

        return self._function_with_leading_comment_after_optional_decorators(updated_node, GET_VALIDATORS_COMMENT)

    def _function_with_leading_comment_after_optional_decorators(
        self, node: cst.FunctionDef, comment: str
    ) -> cst.FunctionDef:
        return node.with_changes(
            lines_after_decorators=[
                *node.lines_after_decorators,
                cst.EmptyLine(comment=cst.Comment(value=(comment))),
                cst.EmptyLine(comment=cst.Comment(value=(CHECK_LINK_COMMENT))),
            ]
        )


if __name__ == "__main__":
    import textwrap

    from rich.console import Console

    console = Console()

    source = textwrap.dedent(
        """
        class SomeThing:
            @classmethod
            def __get_validators__(cls):
                yield from []
                return

            @classmethod
            def __modify_schema__(
                cls, field_schema: Dict[str, Any], field: Optional[ModelField]
            ):
                if field:
                    field_schema['example'] = "Weird example"
        """
    )
    console.print(source)
    console.print("=" * 80)

    mod = cst.parse_module(source)
    context = CodemodContext(filename="main.py")
    wrapper = cst.MetadataWrapper(mod)
    command = CustomTypeCodemod(context=context)
    # console.print(mod)

    mod = wrapper.visit(command)
    wrapper = cst.MetadataWrapper(mod)
    command = AddImportsVisitor(context=context)  # type: ignore[assignment]
    mod = wrapper.visit(command)
    console.print(mod.code)
