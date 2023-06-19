from typing import Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class User(GenericModel, Generic[T]):
    name: str
