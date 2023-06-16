from pathlib import Path

from libcst import MetadataWrapper, parse_module
from libcst.codemod import CodemodContext, CodemodTest
from libcst.metadata import FullyQualifiedNameProvider
from libcst.testing.utils import UnitTest

from bump_pydantic.codemods.class_def_visitor import ClassDefVisitor


class TestClassDefVisitor(UnitTest):
    def gather_class_def(self, file_path: str, code: str) -> ClassDefVisitor:
        mod = MetadataWrapper(
            parse_module(CodemodTest.make_fixture_data(code)),
            cache={
                FullyQualifiedNameProvider: FullyQualifiedNameProvider.gen_cache(Path(""), [file_path], None).get(
                    file_path, ""
                )
            },
        )
        mod.resolve_many(ClassDefVisitor.METADATA_DEPENDENCIES)
        instance = ClassDefVisitor(CodemodContext(wrapper=mod))
        mod.visit(instance)
        return instance

    def test_no_annotations(self) -> None:
        visitor = self.gather_class_def(
            "some/test/module.py",
            """
            def foo() -> None:
                pass
            """,
        )
        results = visitor.context.scratch[ClassDefVisitor.CONTEXT_KEY]
        self.assertEqual(results, {})

    def test_without_bases(self) -> None:
        visitor = self.gather_class_def(
            "some/test/module.py",
            """
            class Foo:
                pass
            """,
        )
        results = visitor.context.scratch[ClassDefVisitor.CONTEXT_KEY]
        self.assertEqual(results, {})

    def test_with_class_defs(self) -> None:
        visitor = self.gather_class_def(
            "some/test/module.py",
            """
            from pydantic import BaseModel

            class Foo(BaseModel):
                pass

            class Bar(Foo):
                pass
            """,
        )
        results = visitor.context.scratch[ClassDefVisitor.CONTEXT_KEY]
        self.assertEqual(
            results,
            {
                "some.test.module.Foo": {"pydantic.BaseModel"},
                "some.test.module.Bar": {"some.test.module.Foo"},
            },
        )

    def test_with_pydantic_base_model(self) -> None:
        visitor = self.gather_class_def(
            "some/test/module.py",
            """
            import pydantic

            class Foo(pydantic.BaseModel):
                ...
            """,
        )
        results = visitor.context.scratch[ClassDefVisitor.CONTEXT_KEY]
        self.assertEqual(
            results,
            {"some.test.module.Foo": {"pydantic.BaseModel"}},
        )
