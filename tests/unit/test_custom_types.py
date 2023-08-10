import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.codemods.validator import ValidatorCodemod

# TODO Use the correct Codemod


class TestArbitraryClassCommand(CodemodTest):
    TRANSFORM = ValidatorCodemod

    maxDiff = None

    @pytest.mark.xfail(reason="Not implemented yet")
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
            # TODO[pydantic]: We couldn't refactor this, please create the `__get_pydantic_core_schema__` manually.
            # Check https://docs.pydantic.dev/latest/migration/#defining-custom-types for more information.
            def __get_validators__(cls):
                yield from []
                return
        """
        self.assertCodemod(before, after)

    @pytest.mark.xfail(reason="Not implemented yet")
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
            # TODO[pydantic]: We couldn't refactor this, please create the `__modify_schema__` manually.
            # Check https://docs.pydantic.dev/latest/migration/#defining-custom-types for more information.
            def __modify_schema__(
                cls, field_schema: Dict[str, Any], field: Optional[ModelField]
            ):
                if field:
                    field_schema['example'] = "Weird example"
        """
        self.assertCodemod(before, after)
