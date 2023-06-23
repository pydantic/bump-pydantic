import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.codemods.replace_config import ReplaceConfigCodemod


class TestReplaceConfigCommand(CodemodTest):
    TRANSFORM = ReplaceConfigCodemod

    maxDiff = None

    def test_config(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_arbitrary_types = True
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(allow_arbitrary_types=True)
        """
        self.assertCodemod(before, after)

    def test_noop_config(self) -> None:
        code = """
        from pydantic import BaseModel

        class Potato:
            class Config:
                allow_mutation = True
        """
        self.assertCodemod(code, code)

    @pytest.mark.xfail(reason="Not implemented yet")
    def test_noop_config_with_bases(self) -> None:
        code = """
        from potato import RandomBase

        class Potato(RandomBase):
            class Config:
                allow_mutation = True
        """
        self.assertCodemod(code, code)

    def test_global_config_class(self) -> None:
        code = """
        from pydantic import BaseModel as Potato

        class Config:
            allow_arbitrary_types = True
        """
        self.assertCodemod(code, code)

    def test_reset_config_args(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_arbitrary_types = True

        potato = Potato()

        class Potato2(BaseModel):
            class Config:
                strict = True
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(allow_arbitrary_types=True)

        potato = Potato()

        class Potato2(BaseModel):
            model_config = ConfigDict(strict=True)
        """
        self.assertCodemod(before, after)

    def test_config_with_non_assign(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_arbitrary_types = True

                def __init__(self):
                    self.allow_mutation = True
        """
        after = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            # TODO[pydantic]: We couldn't refactor this class, please create the `model_config` manually.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
            class Config:
                allow_arbitrary_types = True

                def __init__(self):
                    self.allow_mutation = True
        """
        self.assertCodemod(before, after)

    def test_inherited_config(self) -> None:
        before = """
        from pydantic import BaseModel

        from potato import SuperConfig

        class Potato(BaseModel):
            class Config(SuperConfig):
                allow_arbitrary_types = True
        """
        after = """
        from pydantic import BaseModel

        from potato import SuperConfig

        class Potato(BaseModel):
            # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
            class Config(SuperConfig):
                allow_arbitrary_types = True
        """
        self.assertCodemod(before, after)

    @pytest.mark.xfail(reason="Not implemented yet")
    def test_inner_comments(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                # This is a comment
                allow_arbitrary_types = True
        """
        after = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(
                # This is a comment
                allow_arbitrary_types=True
            )
        """
        self.assertCodemod(before, after)

    def test_already_commented(self) -> None:
        before = """
        from pydantic import BaseModel

        from potato import SuperConfig

        class Potato(BaseModel):
            # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
            class Config(SuperConfig):
                allow_arbitrary_types = True
        """
        after = """
        from pydantic import BaseModel

        from potato import SuperConfig

        class Potato(BaseModel):
            # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
            class Config(SuperConfig):
                allow_arbitrary_types = True
        """
        self.assertCodemod(before, after)

    @pytest.mark.xfail(reason="Not implemented yet")
    def test_extra_enum(self) -> None:
        before = """
        from pydantic import BaseModel, Extra

        class Potato(BaseModel):
            class Config:
                extra = Extra.allow
        """
        after = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(extra="allow")
        """
        self.assertCodemod(before, after)

    def test_removed_keys(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_mutation = True
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            # TODO[pydantic]: The following keys were removed: `allow_mutation`.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
            model_config = ConfigDict(allow_mutation=True)
        """
        self.assertCodemod(before, after)

    def test_multiple_removed_keys(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_mutation = True
                smart_union = True
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            # TODO[pydantic]: The following keys were removed: `allow_mutation`, `smart_union`.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
            model_config = ConfigDict(allow_mutation=True, smart_union=True)
        """
        self.assertCodemod(before, after)

    def test_renamed_keys(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                orm_mode = True
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(from_attributes=True)
        """
        self.assertCodemod(before, after)

    def test_rename_extra_enum_by_string(self) -> None:
        before = """
        from pydantic import BaseModel, Extra

        class Potato(BaseModel):
            class Config:
                extra = Extra.allow
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(extra="allow")
        """
        self.assertCodemod(before, after)

    def test_noop_extra(self) -> None:
        before = """
        from pydantic import BaseModel
        from potato import Extra

        class Potato(BaseModel):
            class Config:
                extra = Extra.potato
        """
        after = """
        from pydantic import ConfigDict, BaseModel
        from potato import Extra

        class Potato(BaseModel):
            model_config = ConfigDict(extra=Extra.potato)
        """
        self.assertCodemod(before, after)

    def test_extra_inside(self) -> None:
        before = """
        from typing import Type

        from pydantic import BaseModel, Extra

        class Model(BaseModel):
            class Config:
                extra = Extra.allow

            def __init_subclass__(cls: "Type[Model]", **kwargs: Any) -> None:
                class Config:
                    extra = Extra.forbid

                cls.Config = Config  # type: ignore
                super().__init_subclass__(**kwargs)
        """
        after = """
        from typing import Type

        from pydantic import ConfigDict, BaseModel, Extra

        class Model(BaseModel):
            model_config = ConfigDict(extra="allow")

            def __init_subclass__(cls: "Type[Model]", **kwargs: Any) -> None:
                class Config:
                    extra = Extra.forbid

                cls.Config = Config  # type: ignore
                super().__init_subclass__(**kwargs)
        """
        self.assertCodemod(before, after)
