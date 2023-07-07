import functools
import logging
import multiprocessing
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Type, TypeVar, Union

import libcst as cst
from libcst.codemod import CodemodContext, ContextAwareTransformer
from libcst.helpers import calculate_module_and_package
from libcst.metadata import FullRepoManager, FullyQualifiedNameProvider, ScopeProvider
from rich.logging import RichHandler
from rich.progress import Progress
from typer import Argument, Exit, Option, Typer, echo
from typing_extensions import ParamSpec

from bump_pydantic import __version__
from bump_pydantic.codemods import Rule, gather_codemods
from bump_pydantic.codemods.mypy_visitor import CONTEXT_KEY, run_mypy_visitor

app = Typer(
    help="Convert Pydantic from V1 to V2 ♻️",
    invoke_without_command=True,
    add_completion=False,
)

P = ParamSpec("P")
T = TypeVar("T")


logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("bump_pydantic")


def version_callback(value: bool):
    if value:
        echo(f"bump-pydantic version: {__version__}")
        raise Exit()


@app.callback()
def main(
    package: Path = Argument(..., exists=True, dir_okay=True, allow_dash=False),
    disable: List[Rule] = Option(default=[], help="Disable a rule."),
    log_file: Path = Option("log.txt", help="Log errors to this file."),
    version: bool = Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
):
    logger.info("Start bump-pydantic.")
    # NOTE: LIBCST_PARSER_TYPE=native is required according to https://github.com/Instagram/LibCST/issues/487.
    os.environ["LIBCST_PARSER_TYPE"] = "native"

    files_str = list(package.glob("**/*.py"))
    files = [str(file.relative_to(".")) for file in files_str]
    logger.info(f"Found {len(files)} files to process.")

    providers = {FullyQualifiedNameProvider, ScopeProvider}
    metadata_manager = FullRepoManager(".", files, providers=providers)  # type: ignore[arg-type]
    metadata_manager.resolve_cache()

    logger.info("Running mypy to get type information. This may take a while...")
    classes = run_mypy_visitor(files)
    scratch: dict[str, Any] = {CONTEXT_KEY: classes}
    logger.info("Finished mypy.")

    start_time = time.time()

    codemods = gather_codemods(disabled=disable)

    log_fp = log_file.open("a+")
    partial_run_codemods = functools.partial(run_codemods, codemods, metadata_manager, scratch, package)
    with Progress(*Progress.get_default_columns(), transient=True) as progress:
        task = progress.add_task(description="Executing codemods...", total=len(files))
        count_errors = 0
        with multiprocessing.Pool() as pool:
            for error in pool.imap_unordered(partial_run_codemods, files):
                progress.advance(task)
                if error is not None:
                    count_errors += 1
                    log_fp.writelines(error)

    modified = [Path(f) for f in files if os.stat(f).st_mtime > start_time]

    if modified:
        logger.info(f"Refactored {len(modified)} files.")

    if count_errors > 0:
        logger.info(f"Found {count_errors} errors. Please check the {log_file} file.")
    else:
        logger.info("Run successfully!")


def run_codemods(
    codemods: List[Type[ContextAwareTransformer]],
    metadata_manager: FullRepoManager,
    scratch: Dict[str, Any],
    package: Path,
    filename: str,
) -> Union[str, None]:
    try:
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

            input_tree = cst.parse_module(code)

            for codemod in codemods:
                transformer = codemod(context=context)
                output_tree = transformer.transform_module(input_tree)
                input_tree = output_tree

            output_code = input_tree.code
            if code != output_code:
                fp.write(output_code)
                fp.truncate()
        return None
    except Exception:
        return f"An error happened on {filename}.\n{traceback.format_exc()}"
