from typing import List, Type

from libcst.codemod import ContextAwareTransformer
from libcst.codemod.visitors import AddImportsVisitor, RemoveImportsVisitor

from bump_pydantic.codemods.add_default_none import AddDefaultNoneCommand
from bump_pydantic.codemods.field import FieldCodemod
from bump_pydantic.codemods.replace_config import ReplaceConfigCodemod
from bump_pydantic.codemods.replace_generic_model import ReplaceGenericModelCommand
from bump_pydantic.codemods.replace_imports import ReplaceImportsCodemod


def gather_codemods() -> List[Type[ContextAwareTransformer]]:
    return [
        AddDefaultNoneCommand,
        ReplaceConfigCodemod,
        FieldCodemod,
        ReplaceImportsCodemod,
        ReplaceGenericModelCommand,
        # RemoveImportsVisitor needs to be the second to last.
        RemoveImportsVisitor,
        # AddImportsVisitor needs to be the last.
        AddImportsVisitor,
    ]
