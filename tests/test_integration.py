import os
from pathlib import Path

from dirty_equals import IsAnyStr
from typer.testing import CliRunner

from bump_pydantic.__main__ import app


def test_integration(tmp_path: Path) -> None:
    runner = CliRunner()
    os.chdir(Path(__file__).parent.parent)
    result = runner.invoke(
        app,
        [
            "project",
            "--diff",
            "--add-default-none",
            "--rename-imports",
            "--rename-methods",
            "--replace-config-class",
            "--replace-config-parameters",
        ],
    )
    assert result.exception is None
    assert result.stdout.splitlines() == [
        "Inferring types... This may take a while.",
        "Types are inferred.",
        # NOTE: Replace `dict` by `model_dump`.
        IsAnyStr(regex=".*/project/rename_method.py"),
        IsAnyStr(regex=".*/project/rename_method.py"),
        "@@ -1,4 +1,4 @@",
        " from project.add_none import A",
        " ",
        " a = A(a=1, b=2, c=3, d=4)",
        "-a.dict()",
        "+a.model_dump()",
        # NOTE: Add `None` to the fields.
        IsAnyStr(regex=".*/project/add_none.py"),
        IsAnyStr(regex=".*/project/add_none.py"),
        "@@ -4,8 +4,8 @@",
        " ",
        " ",
        " class A(BaseModel):",
        "-    a: int | None",
        "-    b: Optional[int]",
        "-    c: Union[int, None]",
        "-    d: Any",
        "+    a: int | None = None",
        "+    b: Optional[int] = None",
        "+    c: Union[int, None] = None",
        "+    d: Any = None",
        "     e: Dict[str, str]",
        "You'll need to manually replace the `Config` class to the `model_config` attribute.",
        IsAnyStr(),
        # NOTE: Rename `Config` class to `model_config` attribute.
        IsAnyStr(regex=".*/project/config_to_model.py"),
        IsAnyStr(regex=".*/project/config_to_model.py"),
        "@@ -1,10 +1,8 @@",
        "-from pydantic import BaseModel",
        "+from pydantic import ConfigDict, BaseModel",
        " ",
        " ",
        " class A(BaseModel):",
        "-    class Config:",
        "-        orm_mode = True",
        "-        validate_all = True",
        "+    model_config = ConfigDict(orm_mode=True, validate_all=True)",
        " ",
        " ",
        " class BaseConfig:",
    ]
