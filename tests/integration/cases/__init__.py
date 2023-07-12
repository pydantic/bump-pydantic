from ..case import Case
from ..file import File
from ..folder import Folder
from .folder_inside_folder import cases as folder_inside_folder_cases
from .get_cases_from_toml_files import cases as toml_cases

cases = [
    Case(
        name="empty",
        source=File("__init__.py", content=[]),
        expected=File("__init__.py", content=[]),
    ),
    *folder_inside_folder_cases,
    *toml_cases,
]
before = Folder("project", *[case.source for case in cases])
expected = Folder("project", *[case.expected for case in cases])
