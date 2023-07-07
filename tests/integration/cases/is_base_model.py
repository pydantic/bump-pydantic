from ..case import Case
from ..file import File

cases = [
    Case(
        id="Make sure is BaseModel",
        input=File(
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
        id="Make sure is BaseModel",
        input=File(
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
        id="Make sure is BaseModel",
        input=File(
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
        id="Make sure is BaseModel",
        input=File(
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
