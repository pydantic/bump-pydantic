from libcst.codemod import CodemodTest

from bump_pydantic.codemods.replace_generic_model import ReplaceGenericModelCommand


class TestReplaceGenericModelCommand(CodemodTest):
    TRANSFORM = ReplaceGenericModelCommand

    def test_noop(self) -> None:
        code = """
        from typing import Generic, TypeVar

        T = TypeVar("T")

        class Potato(Generic[T]):
            ...
        """
        self.assertCodemod(code, code)

    def test_generic_model(self) -> None:
        before = """
        from typing import TypeVar
        from pydantic.generics import GenericModel

        T = TypeVar("T")

        class Potato(GenericModel, Generic[T]):
            ...
        """
        after = """
        from typing import TypeVar
        from pydantic import BaseModel

        T = TypeVar("T")

        class Potato(BaseModel, Generic[T]):
            ...
        """
        self.assertCodemod(before, after)

    def test_generic_model_multiple_bases(self) -> None:
        before = """
        from typing import TypeVar
        from pydantic.generics import GenericModel

        T = TypeVar("T")

        class Potato(GenericModel, Generic[T], object):
            ...
        """
        after = """
        from typing import TypeVar
        from pydantic import BaseModel

        T = TypeVar("T")

        class Potato(BaseModel, Generic[T], object):
            ...
        """
        self.assertCodemod(before, after)

    def test_generic_model_second_base(self) -> None:
        before = """
        from typing import TypeVar
        from pydantic.generics import GenericModel

        T = TypeVar("T")

        class Potato(object, GenericModel, Generic[T]):
            ...
        """
        after = """
        from typing import TypeVar
        from pydantic import BaseModel

        T = TypeVar("T")

        class Potato(object, BaseModel, Generic[T]):
            ...
        """
        self.assertCodemod(before, after)

    def test_generic_model_from_pydantic_import_generics(self) -> None:
        before = """
        from typing import TypeVar
        from pydantic import generics

        T = TypeVar("T")

        class Potato(generics.GenericModel, Generic[T]):
            ...
        """
        after = """
        from typing import TypeVar
        from pydantic import BaseModel

        T = TypeVar("T")

        class Potato(BaseModel, Generic[T]):
            ...
        """
        self.assertCodemod(before, after)
