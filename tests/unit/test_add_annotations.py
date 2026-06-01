import textwrap
from pathlib import Path

import libcst as cst
from libcst import MetadataWrapper, parse_module
from libcst.codemod import CodemodContext, CodemodTest
from libcst.metadata import FullyQualifiedNameProvider
from libcst.testing.utils import UnitTest

from bump_pydantic.codemods.add_annotations import AddAnnotationsCommand
from bump_pydantic.codemods.class_def_visitor import ClassDefVisitor


class TestAddAnnotationsCommand(UnitTest):
    def add_annotations(self, file_path: str, code: str) -> cst.Module:
        mod = MetadataWrapper(
            parse_module(CodemodTest.make_fixture_data(code)),
            cache={
                FullyQualifiedNameProvider: FullyQualifiedNameProvider.gen_cache(
                    Path(""), [file_path], timeout=None
                ).get(file_path, "")
            },
        )
        mod.resolve_many(AddAnnotationsCommand.METADATA_DEPENDENCIES)
        context = CodemodContext(wrapper=mod)
        instance = ClassDefVisitor(context=context)
        mod.visit(instance)

        instance = AddAnnotationsCommand(context=context)  # type: ignore[assignment]
        return mod.visit(instance)

    def test_not_a_model(self) -> None:
        source = textwrap.dedent(
            """
            class Potato:
                a = True
            """
        ).lstrip()
        module = self.add_annotations("some/test/module.py", source)
        assert module.code == source

    def test_has_annotation(self) -> None:
        source = textwrap.dedent(
            """
            from pydantic import BaseModel

            class Potato(BaseModel):
                a: bool = True
            """
        ).lstrip()
        module = self.add_annotations(
            "some/test/module.py",
            source,
        )

        assert module.code == source

    def test_add_annotations(self) -> None:
        source = textwrap.dedent(
            """
            from pydantic import BaseModel, Field

            class Potato(BaseModel):
                name: str
                is_sale = True
                tags = ["tag1", "tag2"]
                price = 10.5
                description = "Some item"
                active = Field(default=True)
                ready = Field(True)
                age = Field(10, title="Age")
                model_config = ConfigDict(from_attributes=True)

                def do_stuff(self):
                    something = [1, 2, 3]
                    return something
            """
        ).lstrip()
        module = self.add_annotations(
            "some/test/module.py",
            source,
        )
        expected = textwrap.dedent(
            """
            from pydantic import BaseModel, Field

            class Potato(BaseModel):
                name: str
                is_sale: bool = True
                # TODO[pydantic]: add type annotation
                tags = ["tag1", "tag2"]
                price: float = 10.5
                description: str = "Some item"
                active: bool = Field(default=True)
                ready: bool = Field(True)
                age: int = Field(10, title="Age")
                model_config = ConfigDict(from_attributes=True)

                def do_stuff(self):
                    something = [1, 2, 3]
                    return something
            """
        ).lstrip()
        assert module.code == expected

    def test_with_multiple_classes(self) -> None:
        source = textwrap.dedent(
            """
            from pydantic import BaseModel, Field

            class Foo(BaseModel):
                name: str
                is_sale = True
                tags = ["tag1", "tag2"]
                price = 10.5
                description = "Some item"
                active = Field(default=True)
                ready = Field(True)
                age = Field(10, title="Age")

            class Bar(Foo):
                sub_name: str
                sub_is_sale = True
                sub_tags = ["tag1", "tag2"]
                sub_price = 10.5
                sub_description = "Some item"
                sub_active = Field(default=True)
                sub_ready = Field(True)
                sub_age = Field(10, title="Age")

                def do_stuff(self):
                    something = [1, 2, 3]
                    return something
            """
        ).lstrip()
        module = self.add_annotations(
            "some/test/module.py",
            source,
        )
        expected = textwrap.dedent(
            """
            from pydantic import BaseModel, Field

            class Foo(BaseModel):
                name: str
                is_sale: bool = True
                # TODO[pydantic]: add type annotation
                tags = ["tag1", "tag2"]
                price: float = 10.5
                description: str = "Some item"
                active: bool = Field(default=True)
                ready: bool = Field(True)
                age: int = Field(10, title="Age")

            class Bar(Foo):
                sub_name: str
                sub_is_sale: bool = True
                # TODO[pydantic]: add type annotation
                sub_tags = ["tag1", "tag2"]
                sub_price: float = 10.5
                sub_description: str = "Some item"
                sub_active: bool = Field(default=True)
                sub_ready: bool = Field(True)
                sub_age: int = Field(10, title="Age")

                def do_stuff(self):
                    something = [1, 2, 3]
                    return something
            """
        ).lstrip()
        assert module.code == expected
