import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.codemods.validator import ValidatorCodemod


class TestValidatorCommand(CodemodTest):
    TRANSFORM = ValidatorCodemod

    maxDiff = None

    def test_rename_validator_to_field_validator(self) -> None:
        before = """
        import typing as t

        from pydantic import BaseModel, validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @validator("name", "dialect", pre=True)
            def _string_validator(cls, v: t.Any) -> t.Optional[str]:
                if isinstance(v, exp.Expression):
                    return v.name.lower()
                return str(v).lower() if v is not None else None
        """
        after = """
        import typing as t

        from pydantic import field_validator, BaseModel


        class Potato(BaseModel):
            name: str
            dialect: str

            @field_validator("name", "dialect", mode="before")
            @classmethod
            def _string_validator(cls, v: t.Any) -> t.Optional[str]:
                if isinstance(v, exp.Expression):
                    return v.name.lower()
                return str(v).lower() if v is not None else None
        """
        self.assertCodemod(before, after)

    def test_use_model_validator(self) -> None:
        before = """
        import typing as t

        from pydantic import BaseModel, root_validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @root_validator(pre=True)
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                if "gateways" not in values and "gateway" in values:
                    values["gateways"] = values.pop("gateway")
        """
        after = """
        import typing as t

        from pydantic import model_validator, BaseModel


        class Potato(BaseModel):
            name: str
            dialect: str

            @model_validator(mode="before")
            @classmethod
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                if "gateways" not in values and "gateway" in values:
                    values["gateways"] = values.pop("gateway")
        """
        self.assertCodemod(before, after)

    def test_remove_allow_reuse_from_model_validator(self) -> None:
        before = """
        import typing as t

        from pydantic import BaseModel, root_validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @root_validator(pre=True, allow_reuse=True)
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                if "gateways" not in values and "gateway" in values:
                    values["gateways"] = values.pop("gateway")
        """
        after = """
        import typing as t

        from pydantic import model_validator, BaseModel


        class Potato(BaseModel):
            name: str
            dialect: str

            @model_validator(mode="before")
            @classmethod
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                if "gateways" not in values and "gateway" in values:
                    values["gateways"] = values.pop("gateway")
        """
        self.assertCodemod(before, after)

    def test_comment_on_validator_with_multiple_params(self) -> None:
        before = """
        import typing as t

        from pydantic import BaseModel, validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @validator("name", "dialect")
            def _string_validator(cls, v: t.Any, values: t.Dict[str, t.Any], **kwargs) -> t.Optional[str]:
                if isinstance(v, exp.Expression):
                    return v.name.lower()
                return str(v).lower() if v is not None else None
        """
        after = """
        import typing as t

        from pydantic import BaseModel, validator


        class Potato(BaseModel):
            name: str
            dialect: str

            # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
            @validator("name", "dialect")
            def _string_validator(cls, v: t.Any, values: t.Dict[str, t.Any], **kwargs) -> t.Optional[str]:
                if isinstance(v, exp.Expression):
                    return v.name.lower()
                return str(v).lower() if v is not None else None
        """

        self.assertCodemod(before, after)

    @pytest.mark.xfail(reason="Not implemented yet")
    def test_reuse_model_validator(self) -> None:
        before = """
        from pydantic import root_validator

        expression_validator = root_validator(pre=True)(parse_expression)
        """
        after = """
        from pydantic import model_validator

        expression_validator = model_validator(mode="before")(parse_expression)
        """
        self.assertCodemod(before, after)

    def test_noop_reuse_validator(self) -> None:
        """Since we don't know if the function has one or more parameters, we can't
        safely replace it with `field_validator`.
        """
        code = """
        from pydantic import validator

        expression_validator = validator(
            "query",
            "expressions_",
            "pre_statements_",
            "post_statements_",
            pre=True,
            allow_reuse=True,
            check_fields=False,
        )(parse_expression)
        """
        self.assertCodemod(code, code)

    def test_root_validator_after(self) -> None:
        before = """
        from pydantic import root_validator, BaseModel


        class Potato(BaseModel):
            name: str
            dialect: str

            @root_validator(pre=False)
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                if "gateways" not in values and "gateway" in values:
                    values["gateways"] = values.pop("gateway")
        """
        after = """
        from pydantic import model_validator, BaseModel


        class Potato(BaseModel):
            name: str
            dialect: str

            @model_validator()
            @classmethod
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                if "gateways" not in values and "gateway" in values:
                    values["gateways"] = values.pop("gateway")
        """
        self.assertCodemod(before, after)

    def test_replace_validator_without_pre(self) -> None:
        before = """
        from pydantic import validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @validator("name", "dialect")
            def _string_validator(cls, v: t.Any) -> t.Optional[str]:
                if isinstance(v, exp.Expression):
                    return v.name.lower()
                return str(v).lower() if v is not None else None
        """
        after = """
        from pydantic import field_validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @field_validator("name", "dialect")
            @classmethod
            def _string_validator(cls, v: t.Any) -> t.Optional[str]:
                if isinstance(v, exp.Expression):
                    return v.name.lower()
                return str(v).lower() if v is not None else None
        """
        self.assertCodemod(before, after)

    def test_replace_validator_with_pre_false(self) -> None:
        before = """
        from pydantic import validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @validator("name", "dialect", pre=False)
            def _string_validator(cls, v: t.Any) -> t.Optional[str]:
                if isinstance(v, exp.Expression):
                    return v.name.lower()
                return str(v).lower() if v is not None else None
        """
        after = """
        from pydantic import field_validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @field_validator("name", "dialect")
            @classmethod
            def _string_validator(cls, v: t.Any) -> t.Optional[str]:
                if isinstance(v, exp.Expression):
                    return v.name.lower()
                return str(v).lower() if v is not None else None
        """
        self.assertCodemod(before, after)

    @pytest.mark.xfail(reason="Not implemented yet")
    def test_import_pydantic(self) -> None:
        before = """
        import typing as t

        import pydantic

        class Potato(pydantic.BaseModel):
            name: str
            dialect: str

            @pydantic.root_validator(pre=True)
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                return values

            @pydantic.validator("name", "dialect")
            def _string_validator(cls, v: t.Any) -> t.Optional[str]:
                return v
        """
        after = """
        import typing as t

        import pydantic


        class Potato(pydantic.BaseModel):
            name: str
            dialect: str

            @pydantic.model_validator(mode="before")
            @classmethod
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                return values

            @pydantic.field_validator("name", "dialect")
            @classmethod
            def _string_validator(cls, v: t.Any) -> t.Optional[str]:
                return v
        """
        self.assertCodemod(before, after)

    @pytest.mark.xfail(reason="Not implemented yet.")
    def test_root_validator_as_cst_name(self) -> None:
        before = """
        import typing as t

        from pydantic import BaseModel, root_validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @root_validator
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                return values
        """
        after = """
        import typing as t

        from pydantic import BaseModel, model_validator


        class Potato(BaseModel):
            name: str
            dialect: str

            @model_validator
            def _normalize_fields(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
                return values
        """
        self.assertCodemod(before, after)

    def test_noop_comment(self) -> None:
        code = """
        import typing as t

        from pydantic import BaseModel, validator


        class Potato(BaseModel):
            name: str
            dialect: str

            # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
            @validator("name", "dialect")
            def _string_validator(cls, v: t.Any, values: t.Dict[str, t.Any], **kwargs) -> t.Optional[str]:
                if isinstance(v, exp.Expression):
                    return v.name.lower()
                return str(v).lower() if v is not None else None
        """
        self.assertCodemod(code, code)
