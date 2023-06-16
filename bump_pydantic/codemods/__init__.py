from typing import List, Type

from libcst.codemod import ContextAwareTransformer
from libcst.codemod.visitors import AddImportsVisitor

from bump_pydantic.codemods.add_default_none import AddDefaultNoneCommand
from bump_pydantic.codemods.replace_imports import ReplaceImportsCodemod


def gather_codemods() -> List[Type[ContextAwareTransformer]]:
    return [
        AddDefaultNoneCommand,
        ReplaceImportsCodemod,
        # AddImportsVisitor needs to be the last.
        AddImportsVisitor,
    ]
