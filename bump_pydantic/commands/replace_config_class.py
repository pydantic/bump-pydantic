from typing import List

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.metadata import PositionProvider
from libcst.codemod.visitors import AddImportsVisitor


base_model_with_config = m.ClassDef(
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
base_model_with_config_child = m.ClassDef(
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


class ReplaceConfigClassByDict(VisitorBasedCodemodCommand):
    """Replace `Config` class by `ConfigDict` call."""

    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.config_args: List[cst.Arg] = []

    @m.visit(m.ClassDef(name=m.Name(value="Config")))
    def visit_config_class(self, node: cst.ClassDef) -> None:
        """Collect the arguments from the `Config` class."""
        for statement in node.body.body:
            if m.matches(statement, m.SimpleStatementLine()):
                statement = cst.ensure_type(statement, cst.SimpleStatementLine)
                for child in statement.body:
                    if m.matches(child, m.Assign()):
                        assignment = cst.ensure_type(child, cst.Assign)
                        assign_target = cst.ensure_type(
                            assignment.targets[0], cst.AssignTarget
                        )
                        keyword = cst.ensure_type(assign_target.target, cst.Name)
                        keyword = keyword.with_changes(value=keyword.value)
                        arg = cst.Arg(
                            value=assignment.value,
                            keyword=keyword,
                            equal=cst.AssignEqual(
                                whitespace_before=cst.SimpleWhitespace(""),
                                whitespace_after=cst.SimpleWhitespace(""),
                            ),
                        )
                        self.config_args.append(arg)

    @m.leave(base_model_with_config_child)
    def leave_config_class_child(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        position = self.get_metadata(PositionProvider, original_node)
        print(
            "You'll need to manually replace the `Config` class to the `model_config` attribute."
        )
        print(f"File: {self.context.filename}:-{position.start.line},{position.start.column}:{position.end.line},{position.end.column}")
        return updated_node

    @m.leave(base_model_with_config)
    def leave_config_class(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        """Replace the `Config` class with a `model_config` attribute.

        Any class that contains a `Config` class will have that class replaced
        with a `model_config` attribute. The `model_config` attribute will be
        assigned a `ConfigDict` object with the same arguments as the attributes
        from `Config` class.
        """
        AddImportsVisitor.add_needed_import(
            context=self.context, module="pydantic", obj="ConfigDict"
        )
        block = cst.ensure_type(original_node.body, cst.IndentedBlock)
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
            )
            if m.matches(statement, m.ClassDef(name=m.Name(value="Config")))
            else statement
            for statement in block.body
        ]
        self.config_args = []
        return updated_node.with_changes(body=updated_node.body.with_changes(body=body))
