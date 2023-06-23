from libcst.codemod import CodemodTest

from bump_pydantic.codemods.root_model import RootModelCommand


class TestReplaceConfigCommand(CodemodTest):
    TRANSFORM = RootModelCommand

    def test_root_model(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            __root__ = int
        """
        after = """
        from pydantic import RootModel

        class Potato(RootModel[int]):
            pass
        """
        self.assertCodemod(before, after)

    def test_noop(self) -> None:
        code = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            pass
        """
        self.assertCodemod(code, code)

    def test_multiple_root_models(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            __root__ = int

        class Carrot(BaseModel):
            __root__ = str
        """
        after = """
        from pydantic import RootModel

        class Potato(RootModel[int]):
            pass

        class Carrot(RootModel[str]):
            pass
        """
        self.assertCodemod(before, after)
