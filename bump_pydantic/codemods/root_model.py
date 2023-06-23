from typing import Union

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor, RemoveImportsVisitor

# Match BaseModel or pydantic.BaseModel
BASE_MODEL_ARG = m.Arg(value=m.Name("BaseModel") | m.Attribute(value=m.Name("pydantic"), attr=m.Name("BaseModel")))
BASE_MODEL_MATCHER = m.ClassDef(bases=[m.ZeroOrMore(), BASE_MODEL_ARG, m.ZeroOrMore()])
# Match the assignment `__root__ = ...`
ROOT_ASSIGNMENT_MATCHER = m.Assign(targets=[m.AssignTarget(target=m.Name("__root__"))])


class RootModelCommand(VisitorBasedCodemodCommand):
    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)

        self.inside_base_model = False
        self.root_type: Union[cst.BaseExpression, None] = None

    @m.visit(BASE_MODEL_MATCHER)
    def visit_base_model(self, node: cst.ClassDef) -> None:
        self.inside_base_model = True

    @m.leave(BASE_MODEL_MATCHER)
    def leave_base_model(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        self.inside_base_model = False
        if self.root_type:
            AddImportsVisitor.add_needed_import(self.context, "pydantic", "RootModel")
            RemoveImportsVisitor.remove_unused_import(self.context, "pydantic", "BaseModel")
            root_slice = cst.SubscriptElement(slice=self.root_type)  # type: ignore[arg-type]
            root_model = cst.Arg(value=cst.Subscript(value=cst.Name("RootModel"), slice=[root_slice]))
            bases = [root_model if m.matches(base, BASE_MODEL_ARG) else base for base in updated_node.bases]
            self.root_type = None
            return updated_node.with_changes(bases=bases)
        return updated_node

    @m.leave(ROOT_ASSIGNMENT_MATCHER)
    def leave_root_assignment(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
        if not self.inside_base_model:
            return updated_node

        self.root_type = updated_node.value
        return cst.RemoveFromParent()  # type: ignore[return-value]


if __name__ == "__main__":
    import textwrap

    from rich.console import Console

    console = Console()

    source = textwrap.dedent(
        """
        from typing import Any, Dict
        from pydantic import BaseModel, Field

        class A(BaseModel):
            __root__ = Dict[str, Dict[str, Any]]
        """
    )
    console.print(source)
    console.print("=" * 80)

    mod = cst.parse_module(source)

    context = CodemodContext(filename="main.py")
    wrapper = cst.MetadataWrapper(mod)
    command = RootModelCommand(context=context)
    mod = wrapper.visit(command)

    wrapper = cst.MetadataWrapper(mod)
    command = AddImportsVisitor(context=context)  # type: ignore[assignment]
    mod = wrapper.visit(command)

    # wrapper = cst.MetadataWrapper(mod)
    # command = RemoveImportsVisitor(context=context)  # type: ignore[assignment]
    # mod = wrapper.visit(command)
    # console.print(mod.code)
