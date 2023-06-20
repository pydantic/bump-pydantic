import difflib
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterator

import libcst as cst
from libcst.codemod import CodemodContext
from libcst.helpers import calculate_module_and_package
from libcst.metadata import (
    FullRepoManager,
    FullyQualifiedNameProvider,
    PositionProvider,
    ScopeProvider,
)
from rich.console import Console
from typer import Argument, Exit, Option, Typer, echo

from bump_pydantic import __version__
from bump_pydantic.codemods import gather_codemods
from bump_pydantic.codemods.class_def_visitor import ClassDefVisitor
from bump_pydantic.markers.find_base_model import find_base_model

app = Typer(help="Convert Pydantic from V1 to V2 ♻️", invoke_without_command=True)


def version_callback(value: bool):
    if value:
        echo(f"bump-pydantic version: {__version__}")
        raise Exit()


@app.callback()
def main(
    package: Path = Argument(..., exists=True, dir_okay=True, allow_dash=False),
    diff: bool = Option(False, help="Show diff instead of applying changes."),
    version: bool = Option(None, "--version", callback=version_callback, is_eager=True),
):
    console = Console()
    files_str = list(package.glob("**/*.py"))
    files = [str(file.relative_to(".")) for file in files_str]

    providers = {ScopeProvider, PositionProvider, FullyQualifiedNameProvider}
    metadata_manager = FullRepoManager(".", files, providers=providers)  # type: ignore[arg-type]
    metadata_manager.resolve_cache()

    scratch: Dict[str, Any] = {}
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

    find_base_model(context=context)  # type: ignore[assignment]
    scratch = context.scratch  # type: ignore[assignment]

    start_time = time.time()

    codemods = gather_codemods()

    # TODO: We can run this in parallel - batch it into files / cores.
    # with ProcessPoolExecutor():
    #     cpu_count = multiprocessing.cpu_count()
    #     batch_size = len(files) // cpu_count + 1

    #     batches = [files[i : i + batch_size] for i in range(0, len(files), batch_size)]
    #     print(batches)

    for codemod in codemods:
        for filename in files:
            module_and_package = calculate_module_and_package(str(package), filename)
            context = CodemodContext(
                metadata_manager=metadata_manager,
                filename=filename,
                full_module_name=module_and_package.name,
                full_package_name=module_and_package.package,
            )
            context.scratch.update(scratch)

            transformer = codemod(context=context)

            old_code = Path(filename).read_text()
            input_tree = cst.parse_module(old_code)
            output_tree = transformer.transform_module(input_tree)

            input_code = input_tree.code
            output_code = output_tree.code

            if input_code != output_code:
                if diff:
                    color_diff(
                        console=console,
                        lines=difflib.unified_diff(
                            input_code.splitlines(keepends=True),
                            output_code.splitlines(keepends=True),
                            fromfile=filename,
                            tofile=filename,
                        ),
                    )
                else:
                    with open(filename, "w") as fp:
                        fp.write(output_tree.code)

    modified = [Path(f) for f in files if os.stat(f).st_mtime > start_time]
    if modified:
        print(f"Refactored {len(modified)} files.")


def color_diff(console: Console, lines: Iterator[str]) -> None:
    for line in lines:
        line = line.rstrip("\n")
        if line.startswith("+"):
            console.print(line, style="green")
        elif line.startswith("-"):
            console.print(line, style="red")
        elif line.startswith("^"):
            console.print(line, style="blue")
        else:
            console.print(line, style="white")
