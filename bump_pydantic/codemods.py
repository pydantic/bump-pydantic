from __future__ import annotations

from pathlib import Path

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.commands.rename import RenameCommand

from bump_pydantic.commands.rename_method_call import RenameMethodCallCommand
from bump_pydantic.commands.replace_call_param import ReplaceCallParam
from bump_pydantic.commands.replace_config_class import ReplaceConfigClassByDict

CHANGED_IMPORTS = {
    "pydantic.tools": "pydantic.deprecated.tools",
    "pydantic.json": "pydantic.deprecated.json",
    "pydantic.parse": "pydantic.deprecated.parse",
    "pydantic.decorator": "pydantic.deprecated.decorator",
    "BaseModel.dict": "BaseModel.model_dump",
}

CHANGED_METHODS = {
    "dict": "model_dump",
    "json": "model_dump_json",
    "parse_obj": "model_validate",
    "construct": "model_construct",
    "schema": "model_json_schema",
    "validate": "model_validate",
    "update_forward_refs": "model_rebuild",
}

CHANGED_CONFIG_PARAMS = {
    "allow_population_by_field_name": "populate_by_name",
    "anystr_lower": "str_to_lower",
    "anystr_strip_whitespace": "str_strip_whitespace",
    "anystr_upper": "str_to_upper",
    "keep_untouched": "ignored_types",
    "max_anystr_length": "str_max_length",
    "min_anystr_length": "str_min_length",
    "orm_mode": "from_attributes",
    "validate_all": "validate_default",
}


def refactor(
    file: Path,
    base_classes: dict[str, list[str]],
    rename_imports: bool = True,
    rename_methods: bool = True,
    replace_config_class: bool = True,
    replace_config_parameters: bool = True,
) -> None:
    """Refactor a file to use the new pydantic API.

    Args:
        file: The file to refactor.
        base_classes: A dictionary with the base classes of a class.
        rename_imports: Whether to rename imports.
        replace_config_class: Whether to replace `Config` class by `ConfigDict`.
        replace_config_parameters: Whether to replace `Config` parameters by `ConfigDict`
            parameters.
    """
    with file.open("w+") as f:
        code = f.read()
        new_code = transform_code(
            code,
            base_classes,
            rename_imports,
            rename_methods,
            replace_config_class,
            replace_config_parameters,
        )
        f.seek(0)
        f.write(new_code)


def transform_code(
    code: str,
    base_classes: dict[str, list[str]],
    rename_imports: bool = True,
    rename_methods: bool = True,
    replace_config_class: bool = True,
    replace_config_parameters: bool = True,
) -> str:
    """Refactor code to use the new pydantic API.

    Args:
        code: The code to refactor.
        base_classes: A dictionary with the base classes of a class.
        rename_imports: Whether to rename imports.
        replace_config_class: Whether to replace `Config` class by `ConfigDict`.
        replace_config_parameters: Whether to replace `Config` parameters by `ConfigDict`
            parameters.

    Returns:
        The refactored code.
    """
    context = CodemodContext(scratch={"base_classes": base_classes})
    mod = cst.parse_module(code)
    transforms: list[VisitorBasedCodemodCommand] = []

    if rename_imports:
        for old_import, new_import in CHANGED_IMPORTS.items():
            transforms.append(RenameCommand(context, old_import, new_import))

    if rename_methods:
        for old_method, new_method in CHANGED_METHODS.items():
            transforms.append(
                RenameMethodCallCommand(
                    context=context,
                    base_classes=("pydantic.BaseModel", "pydantic.main.BaseModel"),
                    old_method=old_method,
                    new_method=new_method,
                )
            )

    if replace_config_class:
        transforms.append(ReplaceConfigClassByDict(context=context))

    if replace_config_parameters:
        for old_param, new_param in CHANGED_CONFIG_PARAMS.items():
            transforms.append(
                ReplaceCallParam(
                    context=context,
                    callers=("pydantic.config.ConfigDict", "pydantic.ConfigDict"),
                    old_param=old_param,
                    new_param=new_param,
                )
            )

    for transform in transforms:
        mod = transform.transform_module(mod)
    return mod.code
