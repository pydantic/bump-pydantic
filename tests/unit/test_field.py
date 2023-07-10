import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.codemods.field import FieldCodemod


class TestFieldCommand(CodemodTest):
    TRANSFORM = FieldCodemod

    maxDiff = None

    def test_field_rename(self) -> None:
        before = """
        from pydantic import BaseModel, Field

        class Potato(BaseModel):
            potato: List[int] = Field(..., min_items=1, max_items=10)
        """
        after = """
        from pydantic import BaseModel, Field

        class Potato(BaseModel):
            potato: List[int] = Field(..., min_length=1, max_length=10)
        """
        self.assertCodemod(before, after)

    def test_noop(self) -> None:
        code = """
        from pydantic import BaseModel
        from potato import Field

        class Potato(BaseModel):
            potato: List[int] = Field(..., max_items=1)
        """
        self.assertCodemod(code, code)

    @pytest.mark.xfail(reason="Not implemented yet")
    def test_field_rename_with_pydantic_import(self) -> None:
        before = """
        import pydantic

        class Potato(pydantic.BaseModel):
            potato: List[int] = pydantic.Field(..., min_items=1, max_items=10)
        """
        after = """
        from pydantic import BaseModel, Field

        class Potato(pydantic.BaseModel):
            potato: List[int] = pydantic.Field(..., min_length=1, max_length=10)
        """
        self.assertCodemod(before, after)

    def test_field_env_on_base_settings(self) -> None:
        before = """
        from pydantic import BaseSettings, Field

        class Settings(BaseSettings):
            potato: int = Field(..., env="POTATO")
        """
        after = """
        from pydantic import BaseSettings, Field

        class Settings(BaseSettings):
            potato: int = Field(..., validation_alias="POTATO")
        """
        self.assertCodemod(before, after)

    @pytest.mark.xfail(reason="Not implemented yet")
    def test_field_noop_on_env_base_model(self) -> None:
        code = """
        from pydantic import BaseModel, Field

        class Potato(BaseModel):
            potato: int = Field(..., env="POTATO")
        """
        self.assertCodemod(code, code)

    def test_replace_const_by_literal_type(self) -> None:
        before = """
        from enum import Enum

        from pydantic import BaseModel, Field


        class MyEnum(Enum):
            POTATO = "potato"

        class Potato(BaseModel):
            potato: MyEnum = Field(MyEnum.POTATO, const=True)
        """
        after = """
        from enum import Enum

        from pydantic import BaseModel
        from typing import Literal


        class MyEnum(Enum):
            POTATO = "potato"

        class Potato(BaseModel):
            potato: Literal[MyEnum.POTATO] = MyEnum.POTATO
        """
        self.assertCodemod(before, after)

    def test_flip_frozen_boolean(self) -> None:
        before = """
        from pydantic import BaseSettings, Field

        class Settings(BaseSettings):
            potato: int = Field(..., allow_mutation=False)
            strawberry: int = Field(..., allow_mutation=True)
        """
        after = """
        from pydantic import BaseSettings, Field

        class Settings(BaseSettings):
            potato: int = Field(..., frozen=True)
            strawberry: int = Field(..., frozen=False)
        """
        self.assertCodemod(before, after)

    def test_annotated_field(self) -> None:
        before = """
        from pydantic import BaseModel, Field
        from typing import Annotated

        class Potato(BaseModel):
            potato: Annotated[List[int], Field(..., min_items=1, max_items=10)]
        """
        after = """
        from pydantic import BaseModel, Field
        from typing import Annotated

        class Potato(BaseModel):
            potato: Annotated[List[int], Field(..., min_length=1, max_length=10)]
        """
        self.assertCodemod(before, after)
