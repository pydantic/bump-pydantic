from __future__ import annotations

import difflib
import functools
import multiprocessing
import os
import time
from pathlib import Path
from typing import Any

import libcst as cst
from libcst.codemod import CodemodContext, ContextAwareTransformer
from libcst.helpers import calculate_module_and_package
from libcst.metadata import (
    FullRepoManager,
    FullyQualifiedNameProvider,
    PositionProvider,
    ScopeProvider,
)
from rich.console import Console
from rich.progress import Progress
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

    scratch: dict[str, Any] = {}
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

    partial_run_codemods = functools.partial(run_codemods, codemods, metadata_manager, scratch, package, diff)
    with Progress(*Progress.get_default_columns(), transient=True) as progress:
        task = progress.add_task(description="Processing...", total=len(files))
        with multiprocessing.Pool() as pool:
            for error_msg in pool.imap_unordered(partial_run_codemods, files):
                progress.update(task, advance=1)
                if isinstance(error_msg, list):
                    color_diff(console, error_msg)

    modified = [Path(f) for f in files if os.stat(f).st_mtime > start_time]
    if modified:
        print(f"Refactored {len(modified)} files.")


def run_codemods(
    codemods: list[type[ContextAwareTransformer]],
    metadata_manager: FullRepoManager,
    scratch: dict[str, Any],
    package: Path,
    diff: bool,
    filename: str,
) -> list[str] | None:
    module_and_package = calculate_module_and_package(str(package), filename)
    context = CodemodContext(
        metadata_manager=metadata_manager,
        filename=filename,
        full_module_name=module_and_package.name,
        full_package_name=module_and_package.package,
    )
    context.scratch.update(scratch)

    file_path = Path(filename)
    with file_path.open("r+") as fp:
        code = fp.read()
        fp.seek(0)

        input_code = str(code)

        for codemod in codemods:
            transformer = codemod(context=context)

            input_tree = cst.parse_module(input_code)
            output_tree = transformer.transform_module(input_tree)

            input_code = output_tree.code

        if code != input_code:
            if diff:
                lines = difflib.unified_diff(
                    code.splitlines(keepends=True),
                    input_code.splitlines(keepends=True),
                    fromfile=filename,
                    tofile=filename,
                )
                return list(lines)
            else:
                fp.write(input_code)
                fp.truncate()

    return None


def color_diff(console: Console, lines: list[str]) -> None:
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
