import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.codemods.field import FieldCodemod


class TestReplaceConfigCommand(CodemodTest):
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
