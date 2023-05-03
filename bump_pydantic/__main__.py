import sys
import difflib
import time
import libcst as cst
from libcst.metadata import ScopeProvider
from libcst.helpers import calculate_module_and_package
from libcst_mypy import MypyTypeInferenceProvider
from libcst.codemod import CodemodContext
from libcst.metadata import FullRepoManager, PositionProvider
import os
from pathlib import Path

from typer import Argument, Typer, Option

from bump_pydantic.transformers import gather_transformers

app = Typer(help="Convert Pydantic from V1 to V2.")


@app.command()
def main(
    package: Path = Argument(..., exists=True, dir_okay=True, allow_dash=False),
    diff: bool = Option(False, help="Show diff instead of applying changes."),
    debug: bool = Option(False, help="Show debug logs."),
    add_default_none: bool = True,
    rename_imports: bool = True,
    rename_methods: bool = True,
    replace_config_class: bool = True,
    replace_config_parameters: bool = True,
) -> None:
    # sourcery skip: hoist-similar-statement-from-if, simplify-len-comparison, swap-nested-ifs
    files = [str(path.absolute()) for path in package.glob("**/*.py")]

    transformers = gather_transformers(
        add_default_none=add_default_none,
        rename_imports=rename_imports,
        rename_methods=rename_methods,
        replace_config_class=replace_config_class,
        replace_config_parameters=replace_config_parameters,
    )

    cwd = os.getcwd()
    providers = {MypyTypeInferenceProvider, ScopeProvider, PositionProvider}
    metadata_manager = FullRepoManager(cwd, files, providers=providers)
    print("Inferring types... This may take a while.")
    metadata_manager.resolve_cache()
    print("Types are inferred.")

    start_time = time.time()

    # TODO: We can run this in parallel - batch it into files / cores.
    # We may need to run the resolve_cache() on each core - not sure.
    for transformer in transformers:
        for filename in files:
            module_and_package = calculate_module_and_package(cwd, filename)
            transform = transformer(
                CodemodContext(
                    metadata_manager=metadata_manager,
                    filename=filename,
                    full_module_name=module_and_package.name,
                    full_package_name=module_and_package.package,
                )
            )
            if debug:
                print(f"Processing {filename} with {transform.__class__.__name__}")

            with open(filename, "r") as fp:
                oldcode = fp.read()

            input_tree = cst.parse_module(oldcode)
            output_tree = transform.transform_module(input_tree)

            input_code = input_tree.code
            output_code = output_tree.code

            if input_code != output_code:
                if diff:
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
    if len(modified) > 0:
        print(f"Refactored {len(modified)} files.")


if __name__ == "__main__":
    app()
