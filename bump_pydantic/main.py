from typer import Argument, Option, Typer, echo, Exit
import time
import sys
import difflib
import libcst as cst
from libcst.helpers import calculate_module_and_package
from libcst.codemod import CodemodContext
import os
from libcst.metadata import (
    FullRepoManager,
    PositionProvider,
    ScopeProvider,
    FullyQualifiedNameProvider,
)
from pathlib import Path
from bump_pydantic.codemods import gather_codemods
from bump_pydantic.codemods.class_def_visitor import ClassDefVisitor
from bump_pydantic import __version__

app = Typer(help="Convert Pydantic from V1 to V2 ♻️", invoke_without_command=True)


def version_callback(value: bool):
    if value:
        echo(f"bump-pydantic version: {__version__}")
        raise Exit()


@app.callback()
def main(
    package: Path = Argument(..., exists=True, dir_okay=True, allow_dash=False),
    version: bool = Option(None, "--version", callback=version_callback, is_eager=True),
    diff: bool = Option(False, help="Show diff instead of applying changes."),
):
    cwd = os.getcwd()
    files = [path.absolute() for path in package.glob("**/*.py")]
    files = [str(file.relative_to(cwd)) for file in files]

    providers = {ScopeProvider, PositionProvider, FullyQualifiedNameProvider}
    metadata_manager = FullRepoManager(cwd, files, providers=providers)
    metadata_manager.resolve_cache()

    scratch = {}
    for filename in files:
        code = Path(filename).read_text()
        module = cst.parse_module(code)
        module_and_package = calculate_module_and_package(str(package), filename)

        context = CodemodContext(
            metadata_manager=metadata_manager,
            filename=filename,
            full_module_name=module_and_package.name,
            full_package_name=module_and_package.package,
            scratch=scratch,
        )
        visitor = ClassDefVisitor(context=context)
        visitor.transform_module(module)
        scratch = context.scratch

    start_time = time.time()

    codemods = gather_codemods()

    # TODO: We can run this in parallel - batch it into files / cores.
    # We may need to run the resolve_cache() on each core - not sure.
    for codemod in codemods:
        for filename in files:
            module_and_package = calculate_module_and_package(str(package), filename)
            transformer = codemod(
                CodemodContext(
                    metadata_manager=metadata_manager,
                    filename=filename,
                    full_module_name=module_and_package.name,
                    full_package_name=module_and_package.package,
                )
            )

            old_code = Path(filename).read_text()
            input_tree = cst.parse_module(old_code)
            output_tree = transformer.transform_module(input_tree)

            input_code = input_tree.code
            output_code = output_tree.code

            if input_code != output_code:
                if diff:
                    # TODO: Should be colored.
                    lines = difflib.unified_diff(
                        input_code.splitlines(keepends=True),
                        output_code.splitlines(keepends=True),
                        fromfile=filename,
                        tofile=filename,
                    )
                    sys.stdout.writelines(lines)
                else:
                    with open(filename, "w") as fp:
                        fp.write(output_tree.code)

    modified = [Path(f) for f in files if os.stat(f).st_mtime > start_time]
    if modified:
        print(f"Refactored {len(modified)} files.")
