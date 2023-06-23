from enum import Enum
from typing import List, Type

from libcst.codemod import ContextAwareTransformer
from libcst.codemod.visitors import AddImportsVisitor, RemoveImportsVisitor

from bump_pydantic.codemods.add_default_none import AddDefaultNoneCommand
from bump_pydantic.codemods.field import FieldCodemod
from bump_pydantic.codemods.replace_config import ReplaceConfigCodemod
from bump_pydantic.codemods.replace_generic_model import ReplaceGenericModelCommand
from bump_pydantic.codemods.replace_imports import ReplaceImportsCodemod
from bump_pydantic.codemods.root_model import RootModelCommand


class Rule(str, Enum):
    BP001 = "BP001"
    """Add default `None` to `Optional[T]`, `Union[T, None]` and `Any` fields"""
    BP002 = "BP002"
    """Replace `Config` class with `model_config` attribute."""
    BP003 = "BP003"
    """Replace `Field` old parameters with new ones."""
    BP004 = "BP004"
    """Replace imports that have been moved."""
    BP005 = "BP005"
    """Replace `GenericModel` with `BaseModel`."""
    BP006 = "BP006"
    """Replace `BaseModel.__root__ = T` with `RootModel[T]`."""


def gather_codemods(disabled: List[Rule]) -> List[Type[ContextAwareTransformer]]:
    codemods: List[Type[ContextAwareTransformer]] = []

    if Rule.BP001 not in disabled:
        codemods.append(AddDefaultNoneCommand)

    if Rule.BP002 not in disabled:
        codemods.append(ReplaceConfigCodemod)

    if Rule.BP003 not in disabled:
        codemods.append(FieldCodemod)

    if Rule.BP004 not in disabled:
        codemods.append(ReplaceImportsCodemod)

    if Rule.BP005 not in disabled:
        codemods.append(ReplaceGenericModelCommand)

    if Rule.BP006 not in disabled:
        codemods.append(RootModelCommand)

    # Those codemods need to be the last ones.
    codemods.extend([RemoveImportsVisitor, AddImportsVisitor])
    return codemods
