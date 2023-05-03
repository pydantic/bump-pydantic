from __future__ import annotations

from typing import Callable

from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.commands.rename import RenameCommand

from bump_pydantic.commands.rename_method_call import RenameMethodCallCommand
from bump_pydantic.commands.replace_call_param import ReplaceCallParam
from bump_pydantic.commands.replace_config_class import ReplaceConfigClassByDict
from bump_pydantic.commands.add_default_none import AddDefaultNoneCommand

CHANGED_IMPORTS = {
    "pydantic.tools": "pydantic.deprecated.tools",
    "pydantic.json": "pydantic.deprecated.json",
    "pydantic.decorator": "pydantic.deprecated.decorator",
    "pydantic.validate_arguments": "pydantic.deprecated.decorator:validate_arguments",
    "pydantic.decorator.validate_arguments": "pydantic.deprecated:decorator.validate_arguments",
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


def gather_transformers(
    add_default_none: bool = True,
    rename_imports: bool = True,
    rename_methods: bool = True,
    replace_config_class: bool = True,
    replace_config_parameters: bool = True,
) -> list[Callable[[CodemodContext], VisitorBasedCodemodCommand]]:
    """Gather all transformers to apply.

    Args:
        add_default_none: Whether to add `None` to fields.
        rename_imports: Whether to rename imports.
        rename_methods: Whether to rename methods.
        replace_config_class: Whether to replace `Config` class by `ConfigDict`.
        replace_config_parameters: Whether to replace `Config` parameters by `ConfigDict`
            parameters.

    Returns:
        A list of transformers to apply.
    """
    transformers: list[Callable[[CodemodContext], VisitorBasedCodemodCommand]] = []

    if rename_methods:
        transformers.append(
            lambda context: RenameMethodCallCommand(
                context=context,
                class_name="pydantic.main.BaseModel",
                methods=CHANGED_METHODS,
            )
        )

    if rename_imports:
        # TODO: This can be a single transformer.
        transformers.extend(
            lambda context: RenameCommand(context, old_import, new_import)
            for old_import, new_import in CHANGED_IMPORTS.items()
        )

    if add_default_none:
        transformers.append(
            lambda context: AddDefaultNoneCommand(
                context=context, class_name="pydantic.main.BaseModel"
            )
        )

    if replace_config_class:
        transformers.append(lambda context: ReplaceConfigClassByDict(context=context))

    if replace_config_parameters:
        transformers.append(
            lambda context: ReplaceCallParam(
                context=context,
                callers=("pydantic.config.ConfigDict", "pydantic.ConfigDict"),
                params=CHANGED_CONFIG_PARAMS,
            )
        )
    return transformers
