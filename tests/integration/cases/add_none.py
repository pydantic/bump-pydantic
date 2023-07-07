from ..case import Case
from ..file import File

cases = [
    Case(
        id="Add None",
        input=File(
            "add_none.py",
            content=[
                "from typing import Any, Dict, Optional, Union",
                "",
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    a: int | None",
                "    b: Optional[int]",
                "    c: Union[int, None]",
                "    d: Any",
                "    e: Dict[str, str]",
            ],
        ),
        expected=File(
            "add_none.py",
            content=[
                "from typing import Any, Dict, Optional, Union",
                "",
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    a: int | None = None",
                "    b: Optional[int] = None",
                "    c: Union[int, None] = None",
                "    d: Any = None",
                "    e: Dict[str, str]",
            ],
        ),
    )
]
