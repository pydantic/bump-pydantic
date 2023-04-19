from __future__ import annotations

import functools

from bump_pydantic.commands.replace_call_param import ReplaceCallParam
from libcst.codemod import CodemodTest


class TestReplaceCallParam(CodemodTest):
    TRANSFORM = ReplaceCallParam

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.customAssert = functools.partial(
            self.assertCodemod,
            callers=("pydantic.ConfigDict", "pydantic.config.ConfigDict"),
            old_param="param",
            new_param="kwarg",
        )

    def test_replace_param(self) -> None:
        before = """
            from pydantic import ConfigDict

            ConfigDict(param="potato")
        """
        after = """
        from pydantic import ConfigDict

        ConfigDict(kwarg="potato")
        """
        self.customAssert(before, after)

    def test_replace_param_with_alias(self) -> None:
        before = """
            from pydantic import ConfigDict as ConfigDicto

            ConfigDicto(param="potato")
        """
        after = """
        from pydantic import ConfigDict as ConfigDicto

        ConfigDicto(kwarg="potato")
        """
        self.customAssert(before, after)

    def test_replace_param_with_import_from(self) -> None:
        before = """
            from pydantic import config

            config.ConfigDict(param="potato")
        """
        after = """
        from pydantic import config

        config.ConfigDict(kwarg="potato")
        """
        self.customAssert(before, after)

    def test_replace_param_with_import_from_as(self) -> None:
        before = """
            from pydantic import config as configo

            configo.ConfigDict(param="potato")
        """
        after = """
        from pydantic import config as configo

        configo.ConfigDict(kwarg="potato")
        """
        self.customAssert(before, after)

    def test_replace_pure_pydantic_import(self) -> None:
        before = """
            import pydantic

            pydantic.ConfigDict(param="potato")
        """
        after = """
        import pydantic

        pydantic.ConfigDict(kwarg="potato")
        """
        self.customAssert(before, after)
