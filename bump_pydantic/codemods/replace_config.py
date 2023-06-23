from typing import List

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor, RemoveImportsVisitor
from libcst.metadata import ClassScope, ScopeProvider

PREFIX_COMMENT = "# TODO[pydantic]: "
REFACTOR_COMMENT = f"{PREFIX_COMMENT}We couldn't refactor this class, please create the `model_config` manually."
REMOVED_KEYS_COMMENT = f"{PREFIX_COMMENT}The following keys were removed: {{keys}}."
INHERIT_CONFIG_COMMENT = f"{PREFIX_COMMENT}The `Config` class inherits from another class, please create the `model_config` manually."  # noqa: E501
CHECK_LINK_COMMENT = "# Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information."

REMOVED_KEYS = [
    "allow_mutation",
    "error_msg_templates",
    "fields",
    "getter_dict",
    "smart_union",
    "underscore_attrs_are_private",
    "json_loads",
    "json_dumps",
    "json_encoders",
    "copy_on_model_validation",
    "post_init_call",
]
RENAMED_KEYS = {
    "allow_population_by_field_name": "populate_by_name",
    "anystr_lower": "str_to_lower",
    "anystr_strip_whitespace": "str_strip_whitespace",
    "anystr_upper": "str_to_upper",
    "keep_untouched": "ignored_types",
    "max_anystr_length": "str_max_length",
    "min_anystr_length": "str_min_length",
    "orm_mode": "from_attributes",
    "schema_extra": "json_schema_extra",
    "validate_all": "validate_default",
}

EXTRA_ATTRIBUTE = m.Attribute(
    value=m.Name("Extra"),
    attr=m.Name(value=m.MatchIfTrue(lambda v: v in ("allow", "forbid", "ignore"))),
)
BASE_MODEL_WITH_CONFIG = m.ClassDef(
    bases=[
        m.ZeroOrMore(),
        m.Arg(),
        m.ZeroOrMore(),
    ],
    body=m.IndentedBlock(
        body=[
            m.ZeroOrMore(),
            m.ClassDef(name=m.Name(value="Config"), bases=[]),
            m.ZeroOrMore(),
        ]
    ),
)
BASE_MODEL_WITH_INHERITED_CONFIG = m.ClassDef(
    bases=[
        m.ZeroOrMore(),
        m.Arg(),
        m.ZeroOrMore(),
    ],
    body=m.IndentedBlock(
        body=[
            m.ZeroOrMore(),
            m.ClassDef(name=m.Name(value="Config"), bases=[m.AtLeastN(n=1)]),
            m.ZeroOrMore(),
        ]
    ),
)
BASE_MODEL_WITH_INVALID_CONFIG = m.ClassDef(
    bases=[
        m.ZeroOrMore(),
        m.Arg(),
        m.ZeroOrMore(),
    ],
    body=m.IndentedBlock(
        body=[
            m.ZeroOrMore(),
            m.ClassDef(
                name=m.Name(value="Config"),
                bases=[],
                body=m.IndentedBlock(
                    body=[
                        m.ZeroOrMore(),
                        m.AtLeastN(n=1, matcher=~m.SimpleStatementLine()),
                        m.ZeroOrMore(),
                    ]
                ),
            ),
            m.ZeroOrMore(),
        ]
    ),
)
"""
This matches a `Config` class with at least one NON `m.SimpleStatementLine`:

Example:
```
class Config:
    allow_mutation = True

    def potato():
        ...
```
"""


class ReplaceConfigCodemod(VisitorBasedCodemodCommand):
    """Replace `Config` class by `ConfigDict` call."""

    METADATA_DEPENDENCIES = (ScopeProvider,)

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)

        self.inside_config_class = False
        self.invalid_config_class = False
        self.inherited_config_class = False
        self.config_args: List[cst.Arg] = []

    @m.visit(m.ClassDef(name=m.Name(value="Config")))
    def visit_config_class(self, node: cst.ClassDef) -> None:
        scope = self.get_metadata(ScopeProvider, node)
        if isinstance(scope, ClassScope):
            self.inside_config_class = True

    @m.leave(m.ClassDef(name=m.Name(value="Config")))
    def leave_config_class(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        self.inside_config_class = False
        if self.invalid_config_class or self.inherited_config_class:
            for line in updated_node.leading_lines:
                if m.matches(line, m.EmptyLine(comment=m.Comment(value=CHECK_LINK_COMMENT))):
                    return updated_node

        if self.invalid_config_class:
            return updated_node.with_changes(
                leading_lines=[
                    *updated_node.leading_lines,
                    cst.EmptyLine(comment=cst.Comment(value=(REFACTOR_COMMENT))),
                    cst.EmptyLine(comment=cst.Comment(value=(CHECK_LINK_COMMENT))),
                ]
            )
        elif self.inherited_config_class:
            return updated_node.with_changes(
                leading_lines=[
                    *updated_node.leading_lines,
                    cst.EmptyLine(comment=cst.Comment(value=(INHERIT_CONFIG_COMMENT))),
                    cst.EmptyLine(comment=cst.Comment(value=(CHECK_LINK_COMMENT))),
                ]
            )
        return updated_node

    def visit_Assign(self, node: cst.Assign) -> None:
        self.assign_value = node.value

    def visit_AssignTarget(self, node: cst.AssignTarget) -> None:
        if self.inside_config_class:
            keyword = RENAMED_KEYS.get(node.target.value, node.target.value)  # type: ignore[attr-defined]
            if m.matches(self.assign_value, EXTRA_ATTRIBUTE):
                value = cst.SimpleString(value=f'"{self.assign_value.attr.value}"')  # type: ignore[attr-defined]
                RemoveImportsVisitor.remove_unused_import(self.context, "pydantic", "Extra")
            else:
                value = self.assign_value  # type: ignore[assignment]
            self.config_args.append(
                cst.Arg(
                    keyword=node.target.with_changes(value=keyword),  # type: ignore[arg-type]
                    value=value,
                    equal=cst.AssignEqual(
                        whitespace_before=cst.SimpleWhitespace(""),
                        whitespace_after=cst.SimpleWhitespace(""),
                    ),
                )
            )

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        return updated_node

    @m.visit(BASE_MODEL_WITH_INHERITED_CONFIG)
    def visit_inherited_config_class(self, node: cst.ClassDef) -> None:
        self.inherited_config_class = True

    @m.leave(BASE_MODEL_WITH_INHERITED_CONFIG)
    def leave_inherited_config_class(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        self.inherited_config_class = False
        return updated_node

    @m.visit(BASE_MODEL_WITH_INVALID_CONFIG)
    def visit_config_class_with_more_than_assignments(self, node: cst.ClassDef) -> None:
        self.invalid_config_class = True

    @m.leave(BASE_MODEL_WITH_CONFIG)
    def leave_config_class_childless(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        """Replace the `Config` class with a `model_config` attribute.

        Any class that contains a `Config` class will have that class replaced
        with a `model_config` attribute. The `model_config` attribute will be
        assigned a `ConfigDict` object with the same arguments as the attributes
        from `Config` class.
        """
        if self.invalid_config_class:
            self.invalid_config_class = False
            return updated_node
        AddImportsVisitor.add_needed_import(context=self.context, module="pydantic", obj="ConfigDict")
        block = cst.ensure_type(updated_node.body, cst.IndentedBlock)
        body = [
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=cst.Name("model_config"))],
                        value=cst.Call(
                            func=cst.Name("ConfigDict"),
                            args=self.config_args,
                        ),
                    )
                ],
                leading_lines=self._leading_lines_from_removed_keys(self.config_args),
            )
            if m.matches(statement, m.ClassDef(name=m.Name(value="Config")))
            else statement
            for statement in block.body
        ]
        self.config_args = []
        return updated_node.with_changes(body=updated_node.body.with_changes(body=body))

    @staticmethod
    def _leading_lines_from_removed_keys(args: List[cst.Arg]) -> List[cst.EmptyLine]:
        removed_keys = [arg.keyword.value for arg in args if arg.keyword.value in REMOVED_KEYS]  # type: ignore
        if not removed_keys:
            return []

        formatted_keys = ", ".join(f"`{key}`" for key in removed_keys)
        return [
            cst.EmptyLine(comment=cst.Comment(value=REMOVED_KEYS_COMMENT.format(keys=formatted_keys))),
            cst.EmptyLine(comment=cst.Comment(value=CHECK_LINK_COMMENT)),
        ]


if __name__ == "__main__":
    import textwrap

    from rich.console import Console

    console = Console()

    source = textwrap.dedent(
        """
        from pydantic import BaseModel

        class A(BaseModel):
            a: str
            # My comment

            b: int

            # potato
            class Config:
                allow_arbitrary_types = True
                schema_extra = {
                    "example": {
                        "foo": "bar",
                    }
                }

                @staticmethod
                def indexes() -> Iterable[Index]:
                    yield Index(DiscoverTopic.org_id, DiscoverTopic.taxonomy_id)
        """
    )
    console.print(source)
    console.print("=" * 80)

    mod = cst.parse_module(source)
    context = CodemodContext(filename="main.py")
    wrapper = cst.MetadataWrapper(mod)
    command = ReplaceConfigCodemod(context=context)
    console.print(mod)

    mod = wrapper.visit(command)
    wrapper = cst.MetadataWrapper(mod)
    command = AddImportsVisitor(context=context)  # type: ignore[assignment]
    mod = wrapper.visit(command)
    console.print(mod.code)
