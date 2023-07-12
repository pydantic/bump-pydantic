from ..case import Case
from ..file import File

cases = [
    Case(
        name="Make sure is BaseModel",
        source=File(
            "a.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    a: int",
                "",
                "",
                "class D:",
                "    d: int",
            ],
        ),
        expected=File(
            "a.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    a: int",
                "",
                "",
                "class D:",
                "    d: int",
            ],
        ),
    ),
    Case(
        name="Make sure is BaseModel",
        source=File(
            "b.py",
            content=[
                "from pydantic import BaseModel",
                "from .a import A, D",
                "from typing import Optional",
                "",
                "",
                "class B(A):",
                "    b: Optional[int]",
                "",
                "",
                "class C(D):",
                "    c: Optional[int]",
            ],
        ),
        expected=File(
            "b.py",
            content=[
                "from pydantic import BaseModel",
                "from .a import A, D",
                "from typing import Optional",
                "",
                "",
                "class B(A):",
                "    b: Optional[int] = None",
                "",
                "",
                "class C(D):",
                "    c: Optional[int]",
            ],
        ),
    ),
    Case(
        name="Make sure is BaseModel",
        source=File(
            "c.py",
            content=[
                "from pydantic import BaseModel",
                "from .d import D",
                "",
                "",
                "class C(D):",
                "    c: Optional[int]",
            ],
        ),
        expected=File(
            "c.py",
            content=[
                "from pydantic import BaseModel",
                "from .d import D",
                "",
                "",
                "class C(D):",
                "    c: Optional[int] = None",
            ],
        ),
    ),
    Case(
        name="Make sure is BaseModel",
        source=File(
            "d.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "",
                "class D(BaseModel):",
                "    d: int",
            ],
        ),
        expected=File(
            "d.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "",
                "class D(BaseModel):",
                "    d: int",
            ],
        ),
    ),
]
