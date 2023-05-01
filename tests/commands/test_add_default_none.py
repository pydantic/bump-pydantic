import textwrap

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
            marks=pytest.mark.xfail(reason="Not implemented yet"),
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
def test_add_default_none(source: str, output: str):
    module = cst.parse_module(textwrap.dedent(source))
    module = module.visit(AddDefaultNoneCommand(context=CodemodContext()))
    assert module.code == textwrap.dedent(output)
