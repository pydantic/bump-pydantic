from __future__ import annotations

from libcst.codemod import CodemodTest

from bump_pydantic.command import BumpPydanticCodemodCommand


class TestPydanticCodemod(CodemodTest):
    TRANSFORM = BumpPydanticCodemodCommand

    def test_config_class_noop(self) -> None:
        before = """
            class Model:
                a: int
                b: int

                class Config:
                    arbitrary_types_allowed = True
            """
        self.assertCodemod(before, before)

    def test_config_class(self) -> None:
        before = """
            from pydantic import BaseModel

            class Model(BaseModel):
                a: int
                b: int

                class Config:
                    arbitrary_types_allowed = True
            """
        after = """
            from pydantic import ConfigDict, BaseModel

            class Model(BaseModel):
                a: int
                b: int
                model_config = ConfigDict(arbitrary_types_allowed=True)
            """
        self.assertCodemod(before, after)

    def test_config_class_at_beginning(self) -> None:
        before = """
            from pydantic import BaseModel

            class Model(BaseModel):
                class Config:
                    arbitrary_types_allowed = True

                a: int
                b: int
            """
        after = """
            from pydantic import ConfigDict, BaseModel

            class Model(BaseModel):
                model_config = ConfigDict(arbitrary_types_allowed=True)

                a: int
                b: int
            """
        self.assertCodemod(before, after)

    def test_config_class_with_base_model_as_alias(self) -> None:
        before = """
            from pydantic import BaseModel as BM

            class Model(BM):
                a: int
                b: int

                class Config:
                    arbitrary_types_allowed = True
            """
        after = """
            from pydantic import ConfigDict, BaseModel as BM

            class Model(BM):
                a: int
                b: int
                model_config = ConfigDict(arbitrary_types_allowed=True)
            """
        self.assertCodemod(before, after)

    def test_config_class_with_pydantic_dot_base_model(self) -> None:
        before = """
            import pydantic

            class Model(pydantic.BaseModel):
                a: int
                b: int

                class Config:
                    arbitrary_types_allowed = True
            """
        after = """
            import pydantic
            from pydantic import ConfigDict

            class Model(pydantic.BaseModel):
                a: int
                b: int
                model_config = ConfigDict(arbitrary_types_allowed=True)
            """
        self.assertCodemod(before, after)

    def test_config_new_attributes(self) -> None:
        before = """
            from pydantic import BaseModel

            class Model(BaseModel):
                a: int
                b: int

                class Config:
                    allow_population_by_field_name = True
                    anystr_lower = True
                    anystr_strip_whitespace = True
                    anystr_upper = True
                    keep_untouched = (int,)
                    max_anystr_length = 10
                    min_anystr_length = 1
                    orm_mode = True
                    validate_all = True
            """
        after = """
            from pydantic import ConfigDict, BaseModel

            class Model(BaseModel):
                a: int
                b: int
                model_config = ConfigDict(populate_by_name=True, str_to_lower=True, str_strip_whitespace=True, str_to_upper=True, ignored_types=(int,), str_max_length=10, str_min_length=1, from_attributes=True, validate_default=True)
            """
        self.assertCodemod(before, after)

    IMPORTS = [
        *[
            (
                f"from pydantic.{module} import {func}",
                f"from pydantic.deprecated.{module} import {func}",
            )
            for module, func in [
                ("tools", "schema_of"),
                ("tools", "schema_json_of"),
                ("tools", "parse_obj_as"),
                ("json", "pydantic_encoder"),
                ("json", "custom_pydantic_decoder"),
                ("json", "timedelta_isoformat"),
                ("decorator", "validate_arguments"),
                ("parse", "load_str_bytes"),
                ("parse", "load_file"),
            ]
        ],
        ("from pydantic import tools", "from pydantic.deprecated import tools"),
        ("from pydantic import json", "from pydantic.deprecated import json"),
        ("from pydantic import parse", "from pydantic.deprecated import parse"),
        ("from pydantic import decorator", "from pydantic.deprecated import decorator"),
        ("from pydantic.tools import *", "from pydantic.deprecated.tools import *"),
    ]

    def test_import_changed(self) -> None:
        for before, after in self.IMPORTS:
            self.assertCodemod(before, after)
