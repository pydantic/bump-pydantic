from ..case import Case
from ..file import File

cases = [
    Case(
        id="BaseSettings import",
        input=File(
            "settings.py",
            content=[
                "from pydantic import BaseSettings",
                "",
                "",
                "class Settings(BaseSettings):",
                "    a: int",
            ],
        ),
        expected=File(
            "settings.py",
            content=[
                "from pydantic_settings import BaseSettings",
                "",
                "",
                "class Settings(BaseSettings):",
                "    a: int",
            ],
        ),
    ),
]
