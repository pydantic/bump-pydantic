"""The codemod that replaces deprecated methods with their new counterparts.

This codemod replaces the following methods:
- `dict` -> `model_dump`
- `json` -> `model_dump_json`
- `parse_obj` -> `model_validate`
- `construct` -> `model_construct`
- `copy` -> `model_copy`
- `schema` -> `model_json_schema`
- `validate` -> `model_validate`

There are two cases this codemod handles:

1. Known BaseModel subclasses:
```py
class A(BaseModel):
    ...

model = A()
model.dict()
```

2. Type annotation:
```py
def func(model: A):
    model.dict()

3. Known BaseModel instance by call inference:
```py
def func() -> A:
    ...

model = func()
model.dict()
```

4. Known BaseModel subclass imported from another module.
```py
from project.add_none import A

model = A()
model.dict()
```

5. Known instance imported from another module.
```py
from project import model

model.dict()
```
"""


from __future__ import annotations

import libcst as cst
import libcst.matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor
from libcst.metadata import QualifiedNameProvider, ScopeProvider

# NOTE: Unsure what do to with the following methods:
# - parse_raw
# - parse_file
# - from_orm
# - schema_json

DEPRECATED_METHODS = {
    "dict": "model_dump",
    "json": "model_dump_json",
    "parse_obj": "model_validate",
    "construct": "model_construct",
    "copy": "model_copy",
    "schema": "model_json_schema",
    "validate": "model_validate",
}

MATCH_DEPRECATED_METHODS = m.Call(
    func=m.Attribute(attr=m.Name(value=m.MatchIfTrue(lambda value: value in DEPRECATED_METHODS)))
)


class ReplaceMethodsCodemod(VisitorBasedCodemodCommand):
    METADATA_DEPENDENCIES = (ScopeProvider, QualifiedNameProvider)

    def visit_AssignTarget(self, node: cst.AssignTarget) -> bool | None:
        print(node)
        return super().visit_AssignTarget(node)

    def visit_Assign(self, node: cst.Assign) -> bool | None:
        print(node)
        return super().visit_Assign(node)

    # TODO: Add a warning in case you find a method that matches the rules, but it's not
    # identified as a BaseModel instance.
    @m.leave(MATCH_DEPRECATED_METHODS)
    def leave_deprecated_methods(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        self.get_metadata(QualifiedNameProvider, original_node)
        # print("hi")
        self.get_metadata(ScopeProvider, original_node)
        # if isinstance(scope, GlobalScope):
        #     print(scope.globals)
        #     print(scope.parent)

        # for assignment in scope.assignments:
        #     if isinstance(assignment, Assignment):
        #         print(assignment.name)
        #         print(assignment.references)
        #         print(assignment.node)
        #         print()
        # scope.get_qualified_names_for(original_node)
        # print(scope.get_qualified_names_for(original_node))
        # for assignment in scope.assignments:
        #     print(assignment.name)
        #     print(assignment.references)
        #     print()
        return updated_node


if __name__ == "__main__":
    import textwrap

    from rich.console import Console

    console = Console()

    source = textwrap.dedent(
        """
        from pydantic import BaseModel

        class A(BaseModel):
            a: int

        class B(A):
            b: int

        model = B(a=1, b=2)
        model.dict()
        """
    )
    console.print(source)
    console.print("=" * 80)

    mod = cst.parse_module(source)
    context = CodemodContext(filename="main.py")
    wrapper = cst.MetadataWrapper(mod)
    command = ReplaceMethodsCodemod(context=context)

    mod = wrapper.visit(command)
    wrapper = cst.MetadataWrapper(mod)
    command = AddImportsVisitor(context=context)  # type: ignore[assignment]
    mod = wrapper.visit(command)
    console.print(mod.code)
