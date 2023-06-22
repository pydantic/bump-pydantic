from libcst.codemod import CodemodTest

from bump_pydantic.codemods.field import FieldCodemod


class TestReplaceConfigCommand(CodemodTest):
    TRANSFORM = FieldCodemod

    maxDiff = None

    def test_field_rename(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            potato: List[int] = Field(..., min_items=1, max_items=10)
        """
        after = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            potato: List[int] = Field(..., min_length=1, max_length=10)
        """
        self.assertCodemod(before, after)
