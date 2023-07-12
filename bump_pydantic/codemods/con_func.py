import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor, RemoveImportsVisitor

CONSTR_CALL = m.Call(func=m.Name("constr") | m.Attribute(value=m.Name("pydantic"), attr=m.Name("constr")))
ANN_ASSIGN_CONSTR_CALL = m.AnnAssign(annotation=m.Annotation(annotation=CONSTR_CALL))


class ConFuncCallCommand(VisitorBasedCodemodCommand):
    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)

    @m.leave(ANN_ASSIGN_CONSTR_CALL)
    def leave_ann_assign_constr_call(self, original_node: cst.AnnAssign, updated_node: cst.AnnAssign) -> cst.AnnAssign:
        AddImportsVisitor.add_needed_import(context=self.context, module="typing_extensions", obj="Annotated")
        annotated = cst.Subscript(
            value=cst.Name("Annotated"),
            slice=[
                cst.SubscriptElement(slice=cst.Index(value=cst.Name("str"))),
                cst.SubscriptElement(slice=cst.Index(value=updated_node.annotation.annotation)),
            ],
        )
        annotation = cst.Annotation(annotation=annotated)
        return updated_node.with_changes(annotation=annotation)

    @m.leave(CONSTR_CALL)
    def leave_constr_call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        RemoveImportsVisitor.remove_unused_import(context=self.context, module="pydantic", obj="constr")
        AddImportsVisitor.add_needed_import(context=self.context, module="pydantic", obj="StringConstraints")
        return updated_node.with_changes(func=cst.Name("StringConstraints"))


if __name__ == "__main__":
    import textwrap

    from rich.console import Console

    console = Console()

    source = textwrap.dedent(
        """
        from pydantic import BaseModel, constr

        class A(BaseModel):
            a: constr(max_length=10)
            b: Annotated[str, StringConstraints(max_length=10)]
        """
    )
    console.print(source)
    console.print("=" * 80)

    mod = cst.parse_module(source)
    context = CodemodContext(filename="main.py")
    wrapper = cst.MetadataWrapper(mod)
    command = ConFuncCallCommand(context=context)
    console.print(mod)

    mod = wrapper.visit(command)
    print(mod.code)
