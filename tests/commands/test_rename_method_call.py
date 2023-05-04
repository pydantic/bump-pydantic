from __future__ import annotations

import textwrap
from pathlib import Path

import libcst as cst
import pytest
from libcst.codemod import CodemodContext
from libcst.metadata import MetadataWrapper
from libcst_mypy import MypyTypeInferenceProvider

from bump_pydantic.commands.rename_method_call import RenameMethodCallCommand


@pytest.mark.parametrize(
    "source, output",
    [
        pytest.param(
            """
            from pydantic import BaseModel

            class Foo(BaseModel):
                bar: str

            foo = Foo(bar="text")
            foo.dict()
            """,
            """
            from pydantic import BaseModel

            class Foo(BaseModel):
                bar: str

            foo = Foo(bar="text")
            foo.model_dump()
            """,
            id="dict",
        ),
        pytest.param(
            """
            class Foo:
                bar: str

            foo = Foo(bar="text")
            foo.dict()
            """,
            """
            class Foo:
                bar: str

            foo = Foo(bar="text")
            foo.dict()
            """,
            id="dict_no_inheritance",
        ),
        pytest.param(
            """
            from pydantic import BaseModel

            class Foo(BaseModel):
                foo: str

            class Bar(Foo):
                bar: str

            bar = Bar(foo="text", bar="text")
            bar.dict()
            """,
            """
            from pydantic import BaseModel

            class Foo(BaseModel):
                foo: str

            class Bar(Foo):
                bar: str

            bar = Bar(foo="text", bar="text")
            bar.model_dump()
            """,
            id="dict_inherited",
        ),
    ],
)
def test_rename_method_call(source: str, output: str, tmp_path: Path) -> None:
    package = tmp_path / "package"
    package.mkdir()

    source_path = package / "a.py"
    source_path.write_text(textwrap.dedent(source))

    file = str(source_path)
    cache = MypyTypeInferenceProvider.gen_cache(package, [file])
    wrapper = MetadataWrapper(
        cst.parse_module(source_path.read_text()),
        cache={MypyTypeInferenceProvider: cache[file]},
    )
    module = wrapper.visit(
        RenameMethodCallCommand(
            context=CodemodContext(wrapper=wrapper),
            class_name="pydantic.main.BaseModel",
            methods={"dict": "model_dump"},
        )
    )
    assert module.code == textwrap.dedent(output)
