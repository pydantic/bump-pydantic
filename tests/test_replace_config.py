from libcst.codemod import CodemodTest

from bump_pydantic.codemods.replace_config import ReplaceConfigCodemod


class TestReplaceConfigCommand(CodemodTest):
    TRANSFORM = ReplaceConfigCodemod

    def test_config(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_arbitrary_types = True
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(allow_arbitrary_types=True)
        """
        self.assertCodemod(before, after)

    def test_noop_config(self) -> None:
        code = """
        from pydantic import BaseModel

        class Potato:
            class Config:
                allow_mutation = True
        """
        self.assertCodemod(code, code)

    def test_global_config_class(self) -> None:
        code = """
        from pydantic import BaseModel as Potato

        class Config:
            allow_arbitrary_types = True
        """
        self.assertCodemod(code, code)

    def test_reset_config_args(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_arbitrary_types = True

        potato = Potato()

        class Potato2(BaseModel):
            class Config:
                allow_mutation = True
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(allow_arbitrary_types=True)

        potato = Potato()

        class Potato2(BaseModel):
            model_config = ConfigDict(allow_mutation=True)
        """
        self.assertCodemod(before, after)
