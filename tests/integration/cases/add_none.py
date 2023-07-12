from ..case import Case
from ..file import File

cases = [
    Case(
        name="Add None",
        source=File(
            "add_none.py",
            content=[
                "from typing import Any, Dict, Optional, Union",
                "",
                "from pydantic import BaseModel, Field",
                "",
                "",
                "class A(BaseModel):",
                "    a: int | None",
                "    b: Optional[int]",
                "    c: Union[int, None]",
                "    d: Any",
                "    e: Dict[str, str]",
                "    f: Optional[int] = Field(..., lt=10)",
                "    g: Optional[int] = Field()",
                "    h: Optional[int] = Field(...)",
                "    i: Optional[int] = Field(default_factory=lambda: None)",
            ],
        ),
        expected=File(
            "add_none.py",
            content=[
                "from typing import Any, Dict, Optional, Union",
                "",
                "from pydantic import BaseModel, Field",
                "",
                "",
                "class A(BaseModel):",
                "    a: int | None = None",
                "    b: Optional[int] = None",
                "    c: Union[int, None] = None",
                "    d: Any = None",
                "    e: Dict[str, str]",
                "    f: Optional[int] = Field(None, lt=10)",
                "    g: Optional[int] = Field(None)",
                "    h: Optional[int] = Field(None)",
                "    i: Optional[int] = Field(default_factory=lambda: None)",
            ],
        ),
    )
]
