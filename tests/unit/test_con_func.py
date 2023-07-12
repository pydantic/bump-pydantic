from libcst.codemod import CodemodTest

from bump_pydantic.codemods.con_func import ConFuncCallCommand


class TestFieldCommand(CodemodTest):
    TRANSFORM = ConFuncCallCommand

    maxDiff = None

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

    def test_pydantic_constr_to_annotated(self) -> None:
        before = """
        import pydantic
        from pydantic import BaseModel

        class Potato(BaseModel):
            potato: pydantic.constr(min_length=1, max_length=10)
        """
        after = """
        import pydantic
        from pydantic import StringConstraints, BaseModel
        from typing_extensions import Annotated

        class Potato(BaseModel):
            potato: Annotated[str, StringConstraints(min_length=1, max_length=10)]
        """
        self.assertCodemod(before, after)
