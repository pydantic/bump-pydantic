import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.codemods.con_func import ConFuncCallCommand


class TestFieldCommand(CodemodTest):
    TRANSFORM = ConFuncCallCommand

    maxDiff = None

    @pytest.mark.xfail(reason="Annotated is not supported yet!")
    def test_constr_to_annotated(self) -> None:
        before = """
        from pydantic import BaseModel, constr

        class Potato(BaseModel):
            potato: constr(min_length=1, max_length=10)
        """
        after = """
        from pydantic import StringConstraints, BaseModel
        from typing_extensions import Annotated

        class Potato(BaseModel):
            potato: Annotated[str, StringConstraints(min_length=1, max_length=10)]
        """
        self.assertCodemod(before, after)

    @pytest.mark.xfail(reason="Annotated is not supported yet!")
    def test_pydantic_constr_to_annotated(self) -> None:
        before = """
        import pydantic
        from pydantic import BaseModel

        class Potato(BaseModel):
            potato: pydantic.constr(min_length=1, max_length=10)
        """
        after = """
        from pydantic import StringConstraints, BaseModel
        from typing_extensions import Annotated

        class Potato(BaseModel):
            potato: Annotated[str, StringConstraints(min_length=1, max_length=10)]
        """
        self.assertCodemod(before, after)

    def test_conlist_to_annotated(self) -> None:
        before = """
        from pydantic import BaseModel, conlist

        class Potato(BaseModel):
            potato: conlist(str, min_items=1, max_items=10)
        """
        after = """
        from pydantic import Field, BaseModel
        from typing import List
        from typing_extensions import Annotated

        class Potato(BaseModel):
            potato: Annotated[List[str], Field(min_items=1, max_items=10)]
        """
        self.assertCodemod(before, after)

    def test_conint_to_annotated(self) -> None:
        before = """
        from pydantic import BaseModel, conint

        class Potato(BaseModel):
            potato: conint(ge=0, le=100)
        """
        after = """
        from pydantic import Field, BaseModel
        from typing_extensions import Annotated

        class Potato(BaseModel):
            potato: Annotated[int, Field(ge=0, le=100)]
        """
        self.assertCodemod(before, after)
