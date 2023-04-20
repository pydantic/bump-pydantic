from __future__ import annotations

import textwrap

import libcst as cst
from libcst.codemod import CodemodContext

from bump_pydantic.collectors.base_classes import BaseClassesCollector


def test_base_classes_collector() -> None:
    first_source = textwrap.dedent(
        """
    from pk.bar import Potato

    class Foo(Potato):
        ...
    """
    )
    second_source = textwrap.dedent(
        """
    from pydantic import BaseModel

    class Potato(BaseModel):
        ...
    """
    )

    base_classes = {}

    module = cst.parse_module(first_source)
    wrapper = cst.MetadataWrapper(module)
    context = CodemodContext(
        filename="pk/foo.py", wrapper=wrapper, full_package_name="pk"
    )
    collector = BaseClassesCollector(context=context)
    wrapper.visit(collector)
    base_classes.update(collector.base_classes)

    module = cst.parse_module(second_source)
    wrapper = cst.MetadataWrapper(module)
    context = CodemodContext(
        filename="pk/bar.py", wrapper=wrapper, full_package_name="pk"
    )
    collector = BaseClassesCollector(context=context)
    wrapper.visit(collector)
    base_classes.update(collector.base_classes)

    assert collector.base_classes == {
        "pk.foo.Foo": ["pk.bar.Potato"],
        "pk.bar.Potato": ["pydantic.BaseModel"],
    }
