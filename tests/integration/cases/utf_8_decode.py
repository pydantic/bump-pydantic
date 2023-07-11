from ..case import Case
from ..file import File

cases = [
    Case(
        id="Test Utf-8",
        input=File(
            "utf_8_test.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "class A(BaseModel):",
                "   pass#testutf8>ščíáýíáýžřčš",
            ],
        ),
        expected=File(
            "add_none.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "class A(BaseModel):",
                "   pass#testutf8>ščíáýíáýžřčš",
            ],
        ),
    )
]
