import difflib
import functools
import multiprocessing
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Type, TypeVar, Union

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
from typing_extensions import ParamSpec

from bump_pydantic import __version__
from bump_pydantic.codemods import gather_codemods
from bump_pydantic.codemods.class_def_visitor import ClassDefVisitor
from bump_pydantic.markers.find_base_model import find_base_model

app = Typer(
    help="Convert Pydantic from V1 to V2 ♻️",
    invoke_without_command=True,
)

P = ParamSpec("P")
T = TypeVar("T")


def version_callback(value: bool):
    if value:
        echo(f"bump-pydantic version: {__version__}")
        raise Exit()


@app.callback()
def main(
    package: Path = Argument(..., exists=True, dir_okay=True, allow_dash=False),
    diff: bool = Option(False, help="Show diff instead of applying changes."),
    log_file: Union[Path, None] = Option(None, help="Log file to write to."),
    version: bool = Option(None, "--version", callback=version_callback, is_eager=True),
):
    console = Console()
    log_fp = log_file.open("a+") if log_file else None

    files_str = list(package.glob("**/*.py"))
    files = [str(file.relative_to(".")) for file in files_str]

    providers = {ScopeProvider, PositionProvider, FullyQualifiedNameProvider}
    metadata_manager = FullRepoManager(".", files, providers=providers)  # type: ignore[arg-type]
    metadata_manager.resolve_cache()

    scratch: dict[str, Any] = {}
    with Progress(*Progress.get_default_columns(), transient=True) as progress:
        task = progress.add_task(description="Running class visitor...", total=len(files))
        with multiprocessing.Pool() as pool:
            partial_visit_class_def = functools.partial(visit_class_def, metadata_manager, str(package))
            for local_scratch in pool.imap_unordered(partial_visit_class_def, files):
                progress.advance(task)
                for key, value in local_scratch.items():
                    scratch.setdefault(key, value).update(value)

    find_base_model(scratch)

    start_time = time.time()

    codemods = gather_codemods()

    partial_run_codemods = functools.partial(run_codemods, codemods, metadata_manager, scratch, package, diff)
    with Progress(*Progress.get_default_columns(), transient=True) as progress:
        task = progress.add_task(description="Processing...", total=len(files))
        with multiprocessing.Pool() as pool:
            for error_msg in pool.imap_unordered(partial_run_codemods, files):
                progress.advance(task)
                if isinstance(error_msg, list):
                    if log_fp is None:
                        color_diff(console, error_msg)
                    else:
                        log_fp.writelines(error_msg)

    modified = [Path(f) for f in files if os.stat(f).st_mtime > start_time]
    if modified:
        print(f"Refactored {len(modified)} files.")

    log_fp.close() if log_fp else None


def visit_class_def(metadata_manager: FullRepoManager, package: str, filename: str) -> Dict[str, Any]:
    code = Path(filename).read_text()
    module = cst.parse_module(code)
    module_and_package = calculate_module_and_package(package, filename)

    context = CodemodContext(
        metadata_manager=metadata_manager,
        filename=filename,
        full_module_name=module_and_package.name,
        full_package_name=module_and_package.package,
    )
    visitor = ClassDefVisitor(context=context)
    visitor.transform_module(module)
    return context.scratch


def capture_exception(func: Callable[P, T]) -> Callable[P, T | str]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | str:
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            func_args = [repr(arg) for arg in args]
            func_kwargs = [f"{key}={repr(value)}" for key, value in kwargs.items()]
            return f"{func.__name__}({', '.join(func_args + func_kwargs)})\n{exc}"

    return wrapper


@capture_exception
def run_codemods(
    codemods: List[Type[ContextAwareTransformer]],
    metadata_manager: FullRepoManager,
    scratch: Dict[str, Any],
    package: Path,
    diff: bool,
    filename: str,
) -> Union[List[str], None]:
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


def color_diff(console: Console, lines: List[str]) -> None:
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
