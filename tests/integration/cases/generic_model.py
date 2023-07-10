from ..case import Case
from ..file import File

cases = [
    Case(
        id="Replace Fields",
        input=File(
            "field.py",
            content=[
                "from pydantic import BaseModel, Field",
                "",
                "",
                "class A(BaseModel):",
                "    a: List[int] = Field(..., min_items=1, max_items=10)",
            ],
        ),
        expected=File(
            "field.py",
            content=[
                "from pydantic import BaseModel, Field",
                "",
                "",
                "class A(BaseModel):",
                "    a: List[int] = Field(..., min_length=1, max_length=10)",
            ],
        ),
    ),
]
