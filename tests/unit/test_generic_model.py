# from pathlib import Path

# import libcst as cst
# from libcst import MetadataWrapper, parse_module
# from libcst.codemod import CodemodContext, CodemodTest
# from libcst.metadata import FullyQualifiedNameProvider

# from bump_pydantic.codemods.add_default_none import AddDefaultNoneCommand
# from bump_pydantic.codemods.mypy_visitor import (
#     GENERIC_MODEL_CONTEXT_KEY,
#     run_mypy_visitor,
# )
# from bump_pydantic.codemods.replace_generic_model import ReplaceGenericModelCommand


# class TestReplaceGenericModelCommand(CodemodTest):
#     TRANSFORM = ReplaceGenericModelCommand

#     def assert_replace_generic_model(self, before: str, after: str) -> None:
#         mod = MetadataWrapper(
#             parse_module(CodemodTest.make_fixture_data(before)),
#             cache={
#                 FullyQualifiedNameProvider: FullyQualifiedNameProvider.gen_cache(Path(""), ["main.py"], None).get(
#                     "main.py", ""
#                 )
#             },
#         )
#         mod.resolve_many(AddDefaultNoneCommand.METADATA_DEPENDENCIES)
#         context = CodemodContext(wrapper=mod)
#         classes = run_mypy_visitor(arg_files=["main.py"])
#         context.scratch.update({GENERIC_MODEL_CONTEXT_KEY: classes})

#         instance = AddDefaultNoneCommand(context=context)  # type: ignore[assignment]
#         self.assertCodeEqual(mod.visit(instance).code, after)

#     def test_noop(self, tmp_path: Path) -> None:
#         code = """
#         from typing import Generic, TypeVar

#         T = TypeVar("T")

#         class Potato(Generic[T]):
#             ...
#         """
#         self.assert_replace_generic_model(code, code)

#     def test_generic_model(self) -> None:
#         before = """
#         from typing import TypeVar
#         from pydantic.generics import GenericModel

#         T = TypeVar("T")

#         class Potato(GenericModel, Generic[T]):
#             ...
#         """
#         after = """
#         from typing import TypeVar
#         from pydantic import BaseModel

#         T = TypeVar("T")

#         class Potato(BaseModel, Generic[T]):
#             ...
#         """
#         self.assertCodemod(before, after)

#     def test_generic_model_multiple_bases(self) -> None:
#         before = """
#         from typing import TypeVar
#         from pydantic.generics import GenericModel

#         T = TypeVar("T")

#         class Potato(GenericModel, Generic[T], object):
#             ...
#         """
#         after = """
#         from typing import TypeVar
#         from pydantic import BaseModel

#         T = TypeVar("T")

#         class Potato(BaseModel, Generic[T], object):
#             ...
#         """
#         self.assertCodemod(before, after)

#     def test_generic_model_second_base(self) -> None:
#         before = """
#         from typing import TypeVar
#         from pydantic.generics import GenericModel

#         T = TypeVar("T")

#         class Potato(object, GenericModel, Generic[T]):
#             ...
#         """
#         after = """
#         from typing import TypeVar
#         from pydantic import BaseModel

#         T = TypeVar("T")

#         class Potato(object, BaseModel, Generic[T]):
#             ...
#         """
#         self.assertCodemod(before, after)

#     def test_generic_model_from_pydantic_import_generics(self) -> None:
#         before = """
#         from typing import TypeVar
#         from pydantic import generics

#         T = TypeVar("T")

#         class Potato(generics.GenericModel, Generic[T]):
#             ...
#         """
#         after = """
#         from typing import TypeVar
#         from pydantic import BaseModel

#         T = TypeVar("T")

#         class Potato(BaseModel, Generic[T]):
#             ...
#         """
#         self.assertCodemod(before, after)

#     def test_generic_model_as_import(self):
#         before = """
#         from typing import TypeVar
#         from pydantic.generics import GenericModel as Potato

#         T = TypeVar("T")

#         class Potato(Potato, Generic[T]):
#             ...
#         """
#         after = """
#         from typing import TypeVar
#         from pydantic import BaseModel

#         T = TypeVar("T")

#         class Potato(BaseModel, Generic[T]):
#             ...
#         """
#         self.assertCodemod(before, after)
