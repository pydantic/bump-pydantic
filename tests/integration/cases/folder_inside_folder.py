from ..case import Case
from ..file import File
from ..folder import Folder

cases = [
    Case(
        id="Add Folder",
        input=Folder(
            "folder",
            File("__init__.py", content=[]),
            File(
                "file.py",
                content=[
                    "from typing import Optional, Union",
                    "",
                    "from .another_module import C",
                    "",
                    "",
                    "class A(C):",
                    "    b: Union[int, None]",
                    "    c: Optional[int]",
                ],
            ),
            File(
                "another_module.py",
                content=[
                    "from pydantic import BaseModel",
                    "",
                    "",
                    "class C(BaseModel):",
                    "    a: int",
                ],
            ),
        ),
        expected=Folder(
            "folder",
            File("__init__.py", content=[]),
            File(
                "file.py",
                content=[
                    "from typing import Optional, Union",
                    "",
                    "from .another_module import C",
                    "",
                    "",
                    "class A(C):",
                    "    b: Union[int, None] = None",
                    "    c: Optional[int] = None",
                ],
            ),
            File(
                "another_module.py",
                content=[
                    "from pydantic import BaseModel",
                    "",
                    "",
                    "class C(BaseModel):",
                    "    a: int",
                ],
            ),
        ),
    )
]
