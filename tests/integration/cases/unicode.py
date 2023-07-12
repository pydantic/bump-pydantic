from ..case import Case
from ..file import File

cases = [
    Case(
        name="Test Utf-8",
        source=File(
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
