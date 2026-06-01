from ..case import Case
from ..file import File
from ..folder import Folder

cases = [
    Case(
        name="Nested Inheritance",
        source=Folder(
            "nested_inheritance",
            File("__init__.py", content=[]),
            File(
                "bar.py",
                content=[
                    "from .foo import Foo",
                    "",
                    "",
                    "class Bar(Foo):",
                    "    b: str | None",
                ],
            ),
            File(
                "baz.py",
                content=[
                    "from .bar import Bar",
                    "",
                    "",
                    "class Baz(Bar):",
                    "    c: str | None",
                ],
            ),
            File(
                "foo.py",
                content=[
                    "from pydantic import BaseModel",
                    "",
                    "",
                    "class Foo(BaseModel):",
                    "    a: str | None",
                ],
            ),
        ),
        expected=Folder(
            "nested_inheritance",
            File("__init__.py", content=[]),
            File(
                "bar.py",
                content=[
                    "from .foo import Foo",
                    "",
                    "",
                    "class Bar(Foo):",
                    "    b: str | None = None",
                ],
            ),
            File(
                "baz.py",
                content=[
                    "from .bar import Bar",
                    "",
                    "",
                    "class Baz(Bar):",
                    "    c: str | None = None",
                ],
            ),
            File(
                "foo.py",
                content=[
                    "from pydantic import BaseModel",
                    "",
                    "",
                    "class Foo(BaseModel):",
                    "    a: str | None = None",
                ],
            ),
        ),
    )
]
