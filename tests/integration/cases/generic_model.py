from ..case import Case
from ..file import File

cases = [
    Case(
        id="Replace GenericModel",
        input=File(
            "noop.py",
            content=[
                "from typing import Generic, TypeVar",
                "",
                "T = TypeVar('T')",
                "",
                "",
                "class Potato(Generic[T]):",
                "    pass",
            ],
        ),
        expected=File(
            "noop.py",
            content=[
                "from typing import Generic, TypeVar",
                "",
                "T = TypeVar('T')",
                "",
                "",
                "class Potato(Generic[T]):",
                "    pass",
            ],
        ),
    ),
]
