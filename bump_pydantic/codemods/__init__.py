from typing import List, Type

from bump_pydantic.codemods.replace_imports import ReplaceImportsCodemod
from libcst.codemod.visitors import AddImportsVisitor
from libcst.codemod import VisitorBasedCodemodCommand

__all__ = ["ReplaceImportsCodemod"]


def gather_codemods() -> List[Type[VisitorBasedCodemodCommand]]:
    return [
        ReplaceImportsCodemod,
        # AddImportsVisitor needs to be the last.
        AddImportsVisitor,
    ]
