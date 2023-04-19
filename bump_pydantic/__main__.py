import functools
import multiprocessing
from pathlib import Path
from typing import List

import libcst as cst
from libcst.codemod import CodemodContext
from typer import Argument, Typer

from bump_pydantic.codemods import refactor
from bump_pydantic.collectors.base_classes import BaseClassesCollector

app = Typer(help="Convert Pydantic from V1 to V2.")


@app.command()
def main(
    files: List[Path] = Argument(..., exists=True, dir_okay=True, allow_dash=True),
    rename_imports: bool = True,
    rename_methods: bool = True,
    replace_config_class: bool = True,
    replace_config_parameters: bool = True,
) -> None:
    base_classes = BaseClassesCollector.visit(files)
    refactor_call = functools.partial(
        refactor,
        base_classes=base_classes,
        rename_imports=rename_imports,
        rename_methods=rename_methods,
        replace_config_class=replace_config_class,
        replace_config_parameters=replace_config_parameters,
    )

    with multiprocessing.Pool() as pool:
        for error_msg in pool.imap_unordered(refactor_call, files):
            if isinstance(error_msg, str):
                print(error_msg)  # noqa
