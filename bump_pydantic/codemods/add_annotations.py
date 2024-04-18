from __future__ import annotations

import libcst as cst
import libcst.matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.metadata import FullyQualifiedNameProvider, QualifiedName

from bump_pydantic.codemods.class_def_visitor import ClassDefVisitor

COMMENT = "# TODO[pydantic]: add type annotation"


class AddAnnotationsCommand(VisitorBasedCodemodCommand):
    """This codemod adds a type annotation or TODO comment to pydantic fields without
    a type annotation.

    Example::
        # Before
        ```py
        from pydantic import BaseModel, Field

        class Foo(BaseModel):
            name: str
            is_sale = True
            tags = ["tag1", "tag2"]
            price = 10.5
            description = "Some item"
            active = Field(default=True)
            ready = Field(True)
            age = Field(10, title="Age")
        ```

        # After
        ```py
        from pydantic import BaseModel, Field

        class Foo(BaseModel):
            name: str
            is_sale: bool = True
            # TODO[pydantic]: add type annotation
            tags = ["tag1", "tag2"]
            price: float = 10.5
            description: str = "Some item"
            active: bool = Field(default=True)
            ready: bool = Field(True)
            age: int = Field(10, title="Age")
        ```
    """

    METADATA_DEPENDENCIES = (FullyQualifiedNameProvider,)

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)

        self.inside_base_model = False
        self.base_model_fields: set[cst.Assign | cst.AnnAssign | cst.SimpleStatementLine] = set()
        self.statement: cst.SimpleStatementLine | None = None
        self.needs_comment = False
        self.has_comment = False
        self.in_field = False

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        fqn_set = self.get_metadata(FullyQualifiedNameProvider, node)

        if not fqn_set:
            return None

        fqn: QualifiedName = next(iter(fqn_set))  # type: ignore
        if fqn.name in self.context.scratch[ClassDefVisitor.BASE_MODEL_CONTEXT_KEY]:
            self.inside_base_model = True
            self.base_model_fields = {
                child for child in node.body.children if isinstance(child, cst.SimpleStatementLine)
            }
            return

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        self.base_model_fields = set()
        return updated_node

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> None:
        if node not in self.base_model_fields:
            return
        if not self.inside_base_model:
            return
        self.statement = node
        self.in_field = True
        for line in node.leading_lines:
            if m.matches(line, m.EmptyLine(comment=m.Comment(value=COMMENT))):
                self.has_comment = True

    def leave_SimpleStatementLine(
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        if original_node not in self.base_model_fields:
            return updated_node
        if self.needs_comment and not self.has_comment:
            updated_node = updated_node.with_changes(
                leading_lines=[
                    *updated_node.leading_lines,
                    cst.EmptyLine(comment=cst.Comment(value=(COMMENT))),
                ],
                body=[
                    *updated_node.body,
                ],
            )
        self.statement = None
        self.needs_comment = False
        self.has_comment = False
        self.in_field = False
        return updated_node

    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign | cst.AnnAssign:
        if not self.in_field:
            return updated_node
        if self.inside_base_model:
            if m.matches(updated_node, m.Assign(targets=[m.AssignTarget(target=m.Name("model_config"))])):
                return updated_node
            Undefined = object()
            value: cst.BaseExpression | object = Undefined
            if m.matches(updated_node.value, m.Call(func=m.Name("Field"))):
                assert isinstance(updated_node.value, cst.Call)
                args = updated_node.value.args
                if args:
                    default_keywords = [arg.value for arg in args if arg.keyword and arg.keyword.value == "default"]
                    # NOTE: It has a "default" value as positional argument.
                    if args[0].keyword is None:
                        value = args[0].value
                    # NOTE: It has a "default" keyword argument.
                    elif default_keywords:
                        value = default_keywords[0]
            else:
                value = updated_node.value
            if value is Undefined:
                self.needs_comment = True
                return updated_node

            # Infer simple type annotations
            ann_type = None
            assert isinstance(value, cst.BaseExpression)
            if m.matches(value, m.Name("True") | m.Name("False")):
                ann_type = "bool"
            elif m.matches(value, m.SimpleString()):
                ann_type = "str"
            elif m.matches(value, m.Integer()):
                ann_type = "int"
            elif m.matches(value, m.Float()):
                ann_type = "float"

            # If there's a simple inferred type annotation, return that
            if ann_type:
                return cst.AnnAssign(
                    target=updated_node.targets[0].target,
                    annotation=cst.Annotation(cst.Name(ann_type)),
                    value=updated_node.value,
                )
            else:
                self.needs_comment = True
        return updated_node
