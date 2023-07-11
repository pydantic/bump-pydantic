from pathlib import Path
from typing import Iterator

try:
    import tomllib  # type: ignore[import]
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

from ..case import Case
from ..file import File


def make_cases(case_dict: dict) -> Iterator[Case]:
    """
    For each test case in a case_dict yield a Case object.
    """
    for filename, value in case_dict.items():
        yield Case(
            name=value["name"],
            source=File(filename, content=value["source"].splitlines()),
            expected=File(filename, content=value["expected"].splitlines()),
        )


def get_cases_from_toml_files() -> Iterator[Case]:
    """
    Read each toml file in this file's directory, create a case_dict, and yield Cases.
    """
    for toml_file in Path(__file__).parent.glob("*.toml"):
        case_dict = tomllib.loads(toml_file.read_text())
        yield from make_cases(case_dict)


cases = get_cases_from_toml_files()
