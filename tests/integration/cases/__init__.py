from ..case import Case
from ..file import File
from ..folder import Folder
from .add_none import cases as add_none_cases
from .base_settings import cases as base_settings_cases
from .con_func import cases as con_func_cases
from .config_to_model import cases as config_to_model_cases
from .custom_types import cases as custom_types_cases
from .field import cases as generic_model_cases
from .folder_inside_folder import cases as folder_inside_folder_cases
from .is_base_model import cases as is_base_model_cases
from .nested_inheritance import cases as nested_inheritance_cases
from .replace_validator import cases as replace_validator_cases
from .root_model import cases as root_model_cases
from .unicode import cases as unicode_cases

cases = [
    Case(
        name="empty",
        source=File("__init__.py", content=[]),
        expected=File("__init__.py", content=[]),
    ),
    *base_settings_cases,
    *add_none_cases,
    *is_base_model_cases,
    *nested_inheritance_cases,
    *replace_validator_cases,
    *config_to_model_cases,
    *root_model_cases,
    *generic_model_cases,
    *folder_inside_folder_cases,
    *unicode_cases,
    *con_func_cases,
    *custom_types_cases,
]
before = Folder("project", *[case.source for case in cases])
expected = Folder("project", *[case.expected for case in cases])
