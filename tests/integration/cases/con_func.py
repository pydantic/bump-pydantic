from ..case import Case
from ..file import File

cases = [
    Case(
        name="Con* functions",
        source=File(
            "con_func.py",
            content=[
                "from pydantic import BaseModel, constr, conlist, conint, conbytes, condecimal, confloat, conset",
                "",
                "",
                "class Potato(BaseModel):",
                "    a: constr(regex='[a-z]+')",
                "    b: conlist(int, min_items=1, max_items=10)",
                "    c: conint(gt=0, lt=10)",
                "    d: conbytes(min_length=1, max_length=10)",
                "    e: condecimal(gt=0, lt=10)",
                "    f: confloat(gt=0, lt=10)",
                "    g: conset(int, min_items=1, max_items=10)",
            ],
        ),
        expected=File(
            "con_func.py",
            content=[
                "from pydantic import Field, BaseModel, constr",
                "from decimal import Decimal",
                "from typing import List, Set",
                "from typing_extensions import Annotated",
                "",
                "",
                "class Potato(BaseModel):",
                "    a: constr(pattern='[a-z]+')",
                "    b: Annotated[List[int], Field(min_length=1, max_length=10)]",
                "    c: Annotated[int, Field(gt=0, lt=10)]",
                "    d: Annotated[bytes, Field(min_length=1, max_length=10)]",
                "    e: Annotated[Decimal, Field(gt=0, lt=10)]",
                "    f: Annotated[float, Field(gt=0, lt=10)]",
                "    g: Annotated[Set[int], Field(min_length=1, max_length=10)]",
            ],
        ),
    )
]
