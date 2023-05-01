import textwrap
from libcst.metadata import MetadataWrapper
from libcst_mypy import MypyTypeInferenceProvider
from pathlib import Path

import libcst as cst
import pytest
from libcst.codemod import CodemodContext

from bump_pydantic.commands.add_default_none import AddDefaultNoneCommand


@pytest.mark.parametrize(
    "source, output",
    [
        pytest.param(
            """
            from typing import Optional

            from pydantic import BaseModel


            class Foo(BaseModel):
                bar: Optional[str]
        """,
            """
            from typing import Optional

            from pydantic import BaseModel


            class Foo(BaseModel):
                bar: Optional[str] = None
        """,
            id="optional",
        ),
        pytest.param(
            """
                import typing
                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: typing.Optional[str]
            """,
            """
                import typing
                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: typing.Optional[str] = None
            """,
            id="typing.optional",
        ),
        pytest.param(
            """
                from typing import Optional

                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: str | None
            """,
            """
                from typing import Optional

                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: str | None = None
            """,
            id="pipe optional",
        ),
        pytest.param(
            """
                from typing import Optional

                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: Union[str, None]
            """,
            """
                from typing import Optional

                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: Union[str, None] = None
            """,
            id="union optional",
        ),
        pytest.param(
            """
                from typing import Any

                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: Any
            """,
            """
                from typing import Any

                from pydantic import BaseModel

                class Foo(BaseModel):
                    bar: Any = None
            """,
            id="any",
        ),
        pytest.param(
            """
                from typing import Any

                from pydantic import BaseModel

                class Foo(BaseModel):
                    ...

                class Bar(Foo):
                    bar: Any
            """,
            """
                from typing import Any

                from pydantic import BaseModel

                class Foo(BaseModel):
                    ...

                class Bar(Foo):
                    bar: Any = None
            """,
            id="inheritance",
        ),
        pytest.param(
            """
                from typing import Any

                class Foo:
                    bar: Any
            """,
            """
                from typing import Any

                class Foo:
                    bar: Any
            """,
            id="not pydantic",
        ),
    ],
)
def test_add_default_none(source: str, output: str, tmp_path: Path) -> None:
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
        AddDefaultNoneCommand(
            context=CodemodContext(), class_name="pydantic.main.BaseModel"
        )
    )
    assert module.code == textwrap.dedent(output)
