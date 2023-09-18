from libcst.codemod import CodemodTest

from bump_pydantic.codemods.custom_types import CustomTypeCodemod


class TestArbitraryClassCommand(CodemodTest):
    TRANSFORM = CustomTypeCodemod

    maxDiff = None

    def test_mark_get_validators(self) -> None:
        before = """
        class SomeThing:
            @classmethod
            def __get_validators__(cls):
                yield from []
                return
        """
        after = """
        class SomeThing:
            @classmethod
            # TODO[pydantic]: We couldn't refactor `__get_validators__`, please create the `__get_pydantic_core_schema__` manually.
            # Check https://docs.pydantic.dev/latest/migration/#defining-custom-types for more information.
            def __get_validators__(cls):
                yield from []
                return
        """  # noqa: E501
        self.assertCodemod(before, after)

    def test_mark_modify_schema(self) -> None:
        before = """
        class SomeThing:
            @classmethod
            def __modify_schema__(
                cls, field_schema: Dict[str, Any], field: Optional[ModelField]
            ):
                if field:
                    field_schema['example'] = "Weird example"
        """
        after = """
        class SomeThing:
            @classmethod
            # TODO[pydantic]: We couldn't refactor `__modify_schema__`, please create the `__get_pydantic_json_schema__` manually.
            # Check https://docs.pydantic.dev/latest/migration/#defining-custom-types for more information.
            def __modify_schema__(
                cls, field_schema: Dict[str, Any], field: Optional[ModelField]
            ):
                if field:
                    field_schema['example'] = "Weird example"
        """  # noqa: E501
        self.assertCodemod(before, after)

    def test_already_commented(self) -> None:
        before = """
        class SomeThing:
            @classmethod
            # TODO[pydantic]: We couldn't refactor `__modify_schema__`, please create the `__get_pydantic_json_schema__` manually.
            # Check https://docs.pydantic.dev/latest/migration/#defining-custom-types for more information.
            def __modify_schema__(
                cls, field_schema: Dict[str, Any], field: Optional[ModelField]
            ):
                if field:
                    field_schema['example'] = "Weird example"
        """  # noqa: E501
        after = """
        class SomeThing:
            @classmethod
            # TODO[pydantic]: We couldn't refactor `__modify_schema__`, please create the `__get_pydantic_json_schema__` manually.
            # Check https://docs.pydantic.dev/latest/migration/#defining-custom-types for more information.
            def __modify_schema__(
                cls, field_schema: Dict[str, Any], field: Optional[ModelField]
            ):
                if field:
                    field_schema['example'] = "Weird example"
        """  # noqa: E501
        self.assertCodemod(before, after)
