from __future__ import annotations

import libcst as cst
import libcst.matchers as m
from libcst.codemod import VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor, RemoveImportsVisitor

GENERIC_MODEL_ARG = m.Arg(value=m.Name("GenericModel")) | m.Arg(
    value=m.Attribute(value=m.Name("generics"), attr=m.Name("GenericModel"))
)


class ReplaceGenericModelCommand(VisitorBasedCodemodCommand):
    @m.leave(m.ClassDef(bases=[m.ZeroOrMore(), GENERIC_MODEL_ARG, m.ZeroOrMore()]))
    def leave_generic_model(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        RemoveImportsVisitor.remove_unused_import(context=self.context, module="pydantic.generics", obj="GenericModel")
        RemoveImportsVisitor.remove_unused_import(context=self.context, module="pydantic", obj="generics")
        AddImportsVisitor.add_needed_import(context=self.context, module="pydantic", obj="BaseModel")
        return updated_node.with_changes(
            bases=[
                base if not m.matches(base, GENERIC_MODEL_ARG) else cst.Arg(value=cst.Name("BaseModel"))
                for base in updated_node.bases
            ]
        )


if __name__ == "__main__":
    import textwrap

    from rich.console import Console

    console = Console()

    source = textwrap.dedent(
        """
        from typing import Generic, TypeVar

        from pydantic.generics import GenericModel

        T = TypeVar("T")

        class Potato(GenericModel, Generic[T]):
            ...
        """
    )
    console.print(source)
    # console.print("=" * 80)

    # mod = cst.parse_module(source)
    # context = CodemodContext(filename="main.py")

    # wrapper = cst.MetadataWrapper(mod)
    # command = ReplaceGenericModelCommand(context=context)
    # mod = wrapper.visit(command)

    # wrapper = cst.MetadataWrapper(mod)
    # command = RemoveImportsVisitor(context=context)  # type: ignore[assignment]
    # mod = wrapper.visit(command)

    # wrapper = cst.MetadataWrapper(mod)
    # command = AddImportsVisitor(context=context)  # type: ignore[assignment]
    # mod = wrapper.visit(command)
    # console.print(mod.code)
