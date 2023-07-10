from ..case import Case
from ..file import File

cases = [
    Case(
        id="Replace __root__ by RootModel",
        input=File(
            "root_model.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    __root__ = int",
            ],
        ),
        expected=File(
            "root_model.py",
            content=[
                "from pydantic import RootModel",
                "",
                "",
                "class A(RootModel[int]):",
                "    pass",
            ],
        ),
    ),
]
