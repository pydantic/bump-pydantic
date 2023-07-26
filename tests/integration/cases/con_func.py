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
                "    h: Optional[conint(ge=1, le=4294967295)] = None",
                "    i: dict[str, condecimal(max_digits=10, decimal_places=2)]",
            ],
        ),
        expected=File(
            "con_func.py",
            content=[
                "from pydantic import Field, StringConstraints, BaseModel",
                "from decimal import Decimal",
                "from typing import List, Set",
                "from typing_extensions import Annotated",
                "",
                "",
                "class Potato(BaseModel):",
                "    a: Annotated[str, StringConstraints(pattern='[a-z]+')]",
                "    b: Annotated[List[int], Field(min_length=1, max_length=10)]",
                "    c: Annotated[int, Field(gt=0, lt=10)]",
                "    d: Annotated[bytes, Field(min_length=1, max_length=10)]",
                "    e: Annotated[Decimal, Field(gt=0, lt=10)]",
                "    f: Annotated[float, Field(gt=0, lt=10)]",
                "    g: Annotated[Set[int], Field(min_length=1, max_length=10)]",
                "    h: Optional[Annotated[int, Field(ge=1, le=4294967295)]] = None",
                "    i: dict[str, Annotated[Decimal, Field(max_digits=10, decimal_places=2)]]",
            ],
        ),
    )
]
