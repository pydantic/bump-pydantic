from ..folder import Folder
from .add_none import cases as add_none_cases
from .base_settings import cases as base_settings_cases
from .config_to_model import cases as config_to_model_cases
from .generic_model import cases as generic_model_cases
from .is_base_model import cases as is_base_model_cases
from .replace_validator import cases as replace_validator_cases
from .root_model import cases as root_model_cases

cases = [
    *base_settings_cases,
    *add_none_cases,
    *is_base_model_cases,
    *replace_validator_cases,
    *config_to_model_cases,
    *root_model_cases,
    *generic_model_cases,
]
before = Folder("project", *[case.input for case in cases])
expected = Folder("project", *[case.expected for case in cases])
