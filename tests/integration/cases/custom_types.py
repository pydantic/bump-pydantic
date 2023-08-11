from ..case import Case
from ..file import File

cases = [
    Case(
        name="Mark __get_validators__",
        source=File(
            "mark_get_validators.py",
            content=[
                "class SomeThing:",
                "    @classmethod",
                "    def __get_validators__(cls):",
                "        yield from []",
                "        return",
            ],
        ),
        expected=File(
            "mark_get_validators.py",
            content=[
                "class SomeThing:",
                "    @classmethod",
                "    # TODO[pydantic]: We couldn't refactor `__get_validators__`, please create the `__get_pydantic_core_schema__` manually.",  # noqa: E501
                "    # Check https://docs.pydantic.dev/latest/migration/#defining-custom-types for more information.",
                "    def __get_validators__(cls):",
                "        yield from []",
                "        return",
            ],
        ),
    ),
    Case(
        name="Mark __modify_schema__",
        source=File(
            "mark_modify_schema.py",
            content=[
                "class SomeThing:",
                "    @classmethod",
                "    def __modify_schema__(",
                "        cls, field_schema: Dict[str, Any], field: Optional[ModelField]",
                "    ):",
                "        if field:",
                "            field_schema['example'] = \"Weird example\"",
            ],
        ),
        expected=File(
            "mark_modify_schema.py",
            content=[
                "class SomeThing:",
                "    @classmethod",
                "    # TODO[pydantic]: We couldn't refactor `__modify_schema__`, please create the `__get_pydantic_json_schema__` manually.",  # noqa: E501
                "    # Check https://docs.pydantic.dev/latest/migration/#defining-custom-types for more information.",
                "    def __modify_schema__(",
                "        cls, field_schema: Dict[str, Any], field: Optional[ModelField]",
                "    ):",
                "        if field:",
                "            field_schema['example'] = \"Weird example\"",
            ],
        ),
    ),
]
