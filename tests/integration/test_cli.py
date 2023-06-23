from __future__ import annotations

import difflib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from bump_pydantic.main import app


class Folder:
    def __init__(self, name: str, *files: Folder | File) -> None:
        self.name = name
        self._files = files

    @property
    def files(self) -> list[Folder | File]:
        return sorted(self._files, key=lambda f: f.name)

    def create_structure(self, root: Path) -> None:
        path = root / self.name
        path.mkdir()

        for file in self.files:
            if isinstance(file, Folder):
                file.create_structure(path)
            else:
                (path / file.name).write_text(file.content)

    @classmethod
    def from_structure(cls, root: Path) -> Folder:
        name = root.name
        files: list[File | Folder] = []

        for path in root.iterdir():
            if path.is_dir():
                files.append(cls.from_structure(path))
            else:
                files.append(File(path.name, path.read_text().splitlines()))

        return Folder(name, *files)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, File):
            return False

        if not isinstance(__value, Folder):
            return NotImplemented

        if self.name != __value.name:
            return False

        if len(self.files) != len(__value.files):
            return False

        for self_file, other_file in zip(self.files, __value.files):
            if self_file != other_file:
                return False

        return True


class File:
    def __init__(self, name: str, content: list[str] | None = None) -> None:
        self.name = name
        self.content = "\n".join(content or [])

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, File):
            return NotImplemented

        if self.name != __value.name:
            return False

        return self.content == __value.content


@pytest.fixture()
def before() -> Folder:
    return Folder(
        "project",
        File("__init__.py"),
        File(
            "settings.py",
            content=[
                "from pydantic import BaseSettings",
                "",
                "",
                "class Settings(BaseSettings):",
                "    a: int",
            ],
        ),
        File(
            "add_none.py",
            content=[
                "from typing import Any, Dict, Optional, Union",
                "",
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    a: int | None",
                "    b: Optional[int]",
                "    c: Union[int, None]",
                "    d: Any",
                "    e: Dict[str, str]",
            ],
        ),
        File(
            "config_to_model.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    class Config:",
                "        orm_mode = True",
                "        validate_all = True",
                "",
                "",
                "class BaseConfig:",
                "    orm_mode = True",
                "    validate_all = True",
                "",
                "",
                "class B(BaseModel):",
                "    class Config(BaseConfig):",
                "        ...",
            ],
        ),
        # File(
        #     "rename_method.py",
        #     content=[
        #         "from project.add_none import A",
        #         "",
        #         'a = A(a=1, b=2, c=3, d=4, e={"ha": "ha"})',
        #         "a.dict()",
        #     ],
        # ),
        File(
            "replace_generic.py",
            content=[
                "from typing import Generic, TypeVar",
                "",
                "from pydantic.generics import GenericModel",
                "",
                "T = TypeVar('T')",
                "",
                "",
                "class User(GenericModel, Generic[T]):",
                "    name: str",
            ],
        ),
        File(
            "field.py",
            content=[
                "from pydantic import BaseModel, Field",
                "",
                "",
                "class A(BaseModel):",
                "    a: List[int] = Field(..., min_items=1, max_items=10)",
            ],
        ),
        File(
            "root_model.py",
            content=[
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    __root__ = int",
            ],
        )
        # File(
        #     "config_dict_and_settings.py",
        #     content=[
        #         "from pydantic import BaseModel, BaseSettings",
        #         "",
        #         "",
        #         "class Settings(BaseSettings):",
        #         "    sentry_dsn: str",
        #         "",
        #         "",
        #         "class A(BaseModel):",
        #         "    class Config:",
        #         "        orm_mode = True",
        #     ]
        # )
    )


@pytest.fixture()
def expected() -> Folder:
    return Folder(
        "project",
        File("__init__.py"),
        File(
            "settings.py",
            content=[
                "from pydantic_settings import BaseSettings",
                "",
                "",
                "class Settings(BaseSettings):",
                "    a: int",
            ],
        ),
        File(
            "add_none.py",
            content=[
                "from typing import Any, Dict, Optional, Union",
                "",
                "from pydantic import BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    a: int | None = None",
                "    b: Optional[int] = None",
                "    c: Union[int, None] = None",
                "    d: Any = None",
                "    e: Dict[str, str]",
            ],
        ),
        File(
            "config_to_model.py",
            content=[
                "from pydantic import ConfigDict, BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    model_config = ConfigDict(from_attributes=True, validate_default=True)",
                "",
                "",
                "class BaseConfig:",
                "    orm_mode = True",
                "    validate_all = True",
                "",
                "",
                "class B(BaseModel):",
                "    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.",  # noqa: E501
                "    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.",
                "    class Config(BaseConfig):",
                "        ...",
            ],
        ),
        # File(
        #     "rename_method.py",
        #     content=[
        #         "from project.add_none import A",
        #         "",
        #         'a = A(a=1, b=2, c=3, d=4, e={"ha": "ha"})',
        #         "a.dict()",
        #     ],
        # ),
        File(
            "replace_generic.py",
            content=[
                "from typing import Generic, TypeVar",
                "from pydantic import BaseModel",
                "",
                "T = TypeVar('T')",
                "",
                "",
                "class User(BaseModel, Generic[T]):",
                "    name: str",
            ],
        ),
        File(
            "field.py",
            content=[
                "from pydantic import BaseModel, Field",
                "",
                "",
                "class A(BaseModel):",
                "    a: List[int] = Field(..., min_length=1, max_length=10)",
            ],
        ),
        File(
            "root_model.py",
            content=[
                "from pydantic import RootModel",
                "",
                "",
                "class A(RootModel[int]):",
                "    pass",
            ],
        )
        # File(
        #     "config_dict_and_settings.py",
        #     content=[
        #         "from pydantic import ConfigDict, BaseModel",
        #         "from pydantic_settings import BaseSettings",
        #         "",
        #         "",
        #         "class Settings(BaseSettings):",
        #         "    sentry_dsn: str",
        #         "",
        #         "",
        #         "class A(BaseModel):",
        #         "    model_config = ConfigDict(orm_mode=True)",
        #     ]
        # )
    )


def find_issue(current: Folder, expected: Folder) -> str:
    for current_file, expected_file in zip(current.files, expected.files):
        if current_file != expected_file:
            if current_file.name != expected_file.name:
                return f"Files have different names: {current_file.name} != {expected_file.name}"
            if isinstance(current_file, Folder) or isinstance(expected_file, Folder):
                return f"One of the files is a folder: {current_file.name} != {expected_file.name}"
            return "\n".join(
                difflib.unified_diff(
                    current_file.content.splitlines(),
                    expected_file.content.splitlines(),
                    fromfile=current_file.name,
                    tofile=expected_file.name,
                )
            )
    return "Unknown"


def test_command_line(tmp_path: Path, before: Folder, expected: Folder) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        before.create_structure(root=Path(td))

        result = runner.invoke(app, [before.name])
        assert result.exit_code == 0, result.output
        # assert result.output.endswith("Refactored 4 files.\n")

        after = Folder.from_structure(Path(td) / before.name)

    assert after == expected, find_issue(after, expected)
