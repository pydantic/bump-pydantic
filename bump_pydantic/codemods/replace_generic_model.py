from __future__ import annotations

import libcst as cst
import libcst.matchers as m
from libcst.codemod import VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor, RemoveImportsVisitor
from libcst.metadata import FullyQualifiedNameProvider, QualifiedName

from bump_pydantic.codemods.mypy_visitor import GENERIC_MODEL_CONTEXT_KEY

GENERIC_MODEL_ARG = m.Arg(value=m.Name("GenericModel")) | m.Arg(
    value=m.Attribute(value=m.Name("generics"), attr=m.Name("GenericModel"))
)


class ReplaceGenericModelCommand(VisitorBasedCodemodCommand):
    METADATA_DEPENDENCIES = (FullyQualifiedNameProvider,)

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        fqn_set = self.get_metadata(FullyQualifiedNameProvider, updated_node)

        if not fqn_set:
            return updated_node

        fqn: QualifiedName = next(iter(fqn_set))  # type: ignore
        if not self.context.scratch[GENERIC_MODEL_CONTEXT_KEY].get(fqn.name, False):
            return updated_node

        RemoveImportsVisitor.remove_unused_import(context=self.context, module="pydantic.generics", obj="GenericModel")
        RemoveImportsVisitor.remove_unused_import(context=self.context, module="pydantic", obj="generics")
        AddImportsVisitor.add_needed_import(context=self.context, module="pydantic", obj="BaseModel")

        bases: list[cst.Arg] = []
        for base in updated_node.bases:
            fqn_base_set = self.get_metadata(FullyQualifiedNameProvider, base)
            if not fqn_base_set:
                bases.append(base)
                continue

            fqn_base: QualifiedName = next(iter(fqn_base_set))  # type: ignore
            if self.context.scratch[GENERIC_MODEL_CONTEXT_KEY].get(fqn_base.name, False):
                bases.append(cst.Arg(value=cst.Name("BaseModel")))
            else:
                bases.append(base)
        return updated_node.with_changes(bases=bases)


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
