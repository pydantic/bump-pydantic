from ..case import Case
from ..file import File

cases = [
    Case(
        id="Test Utf-8",
        input=File(
            "unicode.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    pass  # some unicode: ščíáýíáýžřčš ♻️",
            ],
        ),
        expected=File(
            "unicode.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    pass  # some unicode: ščíáýíáýžřčš ♻️",
            ],
        ),
    )
]
