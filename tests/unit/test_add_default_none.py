import textwrap
from pathlib import Path

import libcst as cst
import pytest
from libcst import MetadataWrapper, parse_module
from libcst.codemod import CodemodContext, CodemodTest
from libcst.metadata import FullyQualifiedNameProvider
from libcst.testing.utils import UnitTest

from bump_pydantic.codemods.add_default_none import AddDefaultNoneCommand
from bump_pydantic.codemods.class_def_visitor import ClassDefVisitor


class TestClassDefVisitor(UnitTest):
    def add_default_none(self, file_path: str, code: str) -> cst.Module:
        mod = MetadataWrapper(
            parse_module(CodemodTest.make_fixture_data(code)),
            cache={
                FullyQualifiedNameProvider: FullyQualifiedNameProvider.gen_cache(
                    Path(""), [file_path], timeout=None
                ).get(file_path, "")
            },
        )
        mod.resolve_many(AddDefaultNoneCommand.METADATA_DEPENDENCIES)
        context = CodemodContext(wrapper=mod)
        instance = ClassDefVisitor(context=context)
        mod.visit(instance)

        instance = AddDefaultNoneCommand(context=context)  # type: ignore[assignment]
        return mod.visit(instance)

    def test_no_annotations(self) -> None:
        source = textwrap.dedent(
            """class Potato:
            a: Optional[str]
        """
        )
        module = self.add_default_none("some/test/module.py", source)
        assert module.code == source

    def test_with_optional(self) -> None:
        module = self.add_default_none(
            "some/test/module.py",
            """
            from pydantic import BaseModel

            class Potato(BaseModel):
                a: Optional[str]
            """,
        )
        expected = textwrap.dedent(
            """from pydantic import BaseModel

class Potato(BaseModel):
    a: Optional[str] = None
"""
        )
        assert module.code == expected

    def test_with_union_none(self) -> None:
        module = self.add_default_none(
            "some/test/module.py",
            """
            from pydantic import BaseModel
            from typing import Union

            class Potato(BaseModel):
                a: Union[str, None]
            """,
        )
        expected = textwrap.dedent(
            """from pydantic import BaseModel
from typing import Union

class Potato(BaseModel):
    a: Union[str, None] = None
"""
        )
        assert module.code == expected

    def test_with_multiple_classes(self) -> None:
        module = self.add_default_none(
            "some/test/module.py",
            """
            from pydantic import BaseModel
            from typing import Optional

            class Potato(BaseModel):
                a: Optional[str]

            class Carrot(Potato):
                b: Optional[str]
            """,
        )
        expected = textwrap.dedent(
            """from pydantic import BaseModel
from typing import Optional

class Potato(BaseModel):
    a: Optional[str] = None

class Carrot(Potato):
    b: Optional[str] = None
            """
        )
        assert module.code == expected

    def test_any(self) -> None:
        module = self.add_default_none(
            "some/test/module.py",
            """
            from pydantic import BaseModel
            from typing import Any

            class Potato(BaseModel):
                a: Any
            """,
        )
        expected = textwrap.dedent(
            """from pydantic import BaseModel
from typing import Any

class Potato(BaseModel):
    a: Any = None
"""
        )
        assert module.code == expected

    @pytest.mark.xfail(reason="Recursive Union is not supported")
    def test_union_of_union(self) -> None:
        module = self.add_default_none(
            "some/test/module.py",
            """
            from pydantic import BaseModel
            from typing import Union

            class Potato(BaseModel):
                a: Union[Union[str, None], int]
            """,
        )
        expected = textwrap.dedent(
            """from pydantic import BaseModel
from typing import Union

class Potato(BaseModel):
    a: Union[Union[str, None], int] = None
"""
        )
        assert module.code == expected
