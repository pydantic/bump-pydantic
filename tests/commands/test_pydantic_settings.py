import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.commands.use_settings import UsePydanticSettingsCommand


class TestUsePydanticSettingsCommand(CodemodTest):
    TRANSFORM = lambda _, context: UsePydanticSettingsCommand(context)

    def test_base_settings(self):
        before = """
            from pydantic import BaseSettings

            class Settings(BaseSettings):
                foo: str
            """
        after = """
            from pydantic_settings import BaseSettings

            class Settings(BaseSettings):
                foo: str
            """
        self.assertCodemod(before, after)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_base_settings_import(self):
        before = """
            from pydantic.settings import BaseSettings

            class Settings(BaseSettings):
                foo: str
            """
        after = """
            from pydantic_settings import BaseSettings

            class Settings(BaseSettings):
                foo: str
            """
        self.assertCodemod(before, after)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_base_settings_import_from(self):
        before = """
            import pydantic

            class Settings(pydantic.BaseSettings):
                foo: str
            """
        after = """
            from pydantic_settings import BaseSettings

            class Settings(BaseSettings):
                foo: str
            """
        self.assertCodemod(before, after)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_base_settings_import_from_alias(self):
        before = """
            import pydantic as pd

            class Settings(pd.BaseSettings):
                foo: str
            """
        after = """
            from pydantic_settings import BaseSettings

            class Settings(BaseSettings):
                foo: str
            """
        self.assertCodemod(before, after)
