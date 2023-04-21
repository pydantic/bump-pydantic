from __future__ import annotations

import functools

from libcst.codemod import CodemodTest
from pydantic import BaseModel

from bump_pydantic.commands.rename_method_call import RenameMethodCallCommand


class TestRenameMethodCommand(CodemodTest):
    TRANSFORM = RenameMethodCallCommand

    def test_rename_method_simple_case(self):
        before = """
            from pydantic import BaseModel

            class Foo(BaseModel):
                bar: str

            foo = Foo(bar="text")
            foo.dict()
        """
        after = """
            from pydantic import BaseModel

            class Foo(BaseModel):
                bar: str

            foo = Foo(bar="text")
            foo.model_dump()
        """
        self.assertCodemod(
            before,
            after,
            classes=("pydantic.BaseModel", "pydantic.main.BaseModel"),
            old_method="dict",
            new_method="model_dump",
        )
