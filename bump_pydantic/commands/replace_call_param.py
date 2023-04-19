"""Replace a parameter in a function call."""
from __future__ import annotations

import libcst as cst
import libcst.matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.metadata import ImportAssignment, ScopeProvider


class ReplaceCallParam(VisitorBasedCodemodCommand):
    """Replace a parameter in a function call.

    We visit the call to check if it's one of the callers provided, and if so,
    we visit the arguments to check if it's the old parameter. If so, we replace
    it with the new parameter.
    """

    METADATA_DEPENDENCIES = (ScopeProvider,)

    def __init__(
        self,
        context: CodemodContext,
        callers: tuple[str, ...],
        old_param: str,
        new_param: str,
    ) -> None:
        super().__init__(context)
        self.callers = callers
        self.old_param = old_param
        self.new_param = new_param

        self.inside_caller = False

    def visit_Call(self, node: cst.Call) -> None:
        scope = self.get_metadata(ScopeProvider, node)
        if scope is None:
            return
        for assignment in scope.assignments:
            if isinstance(assignment, ImportAssignment):
                qualified_names = assignment.get_qualified_names_for(assignment.name)
                print(qualified_names)
                if any(qn.name in self.callers for qn in qualified_names):
                    self.inside_caller = True

    def leave_Call(self, _: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:
        self.inside_caller = False
        return updated_node

    def leave_Arg(self, _: cst.Arg, updated_node: cst.Arg) -> cst.Arg:
        is_old_param = m.matches(updated_node, m.Arg(keyword=m.Name(self.old_param)))
        if self.inside_caller and is_old_param:
            return updated_node.with_changes(keyword=cst.Name(self.new_param))
        return updated_node


if __name__ == "__main__":
    import textwrap

    from rich.console import Console

    console = Console()

    source = textwrap.dedent(
        """
    from pydantic.config import ConfigDict as ConfigDicto

    ConfigDicto(potato="potato")
    """
    )
    console.print(source)
    console.print("=" * 80)

    mod = cst.parse_module(source)
    context = CodemodContext(filename="test.py")
    wrapper = cst.MetadataWrapper(mod)
    command = ReplaceCallParam(
        context=context,
        callers=("pydantic.ConfigDict", "pydantic.config.ConfigDict"),
        old_param="potato",
        new_param="tomato",
    )
    mod = wrapper.visit(command)
    console.print(mod.code)
