from __future__ import annotations

import difflib
from pathlib import Path

from typer.testing import CliRunner

from bump_pydantic.main import app

from .cases import before, expected
from .folder import Folder


def find_issue(current: Folder, expected: Folder) -> str:
    for current_file, expected_file in zip(current.files, expected.files):
        if current_file != expected_file:
            if current_file.name != expected_file.name:
                return f"Files have different names: {current_file.name} != {expected_file.name}"
            if isinstance(current_file, Folder) and isinstance(expected_file, Folder):
                return find_issue(current_file, expected_file)
            elif isinstance(current_file, Folder) or isinstance(expected_file, Folder):
                return f"One of the files is a folder: {current_file.name} != {expected_file.name}"
            return "\n".join(
                difflib.unified_diff(
                    current_file.content.splitlines(),
                    expected_file.content.splitlines(),
                    fromfile=current_file.name,
                    tofile=expected_file.name,
                )
            )
    return "Unknown"


# @pytest.mark.parametrize("before,expected", zip([before, expected]))
def test_command_line(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        before.create_structure(root=Path(td))

        result = runner.invoke(app, [before.name])
        assert result.exit_code == 0, result.output
        # assert result.output.endswith("Refactored 4 files.\n")

        after = Folder.from_structure(Path(td) / before.name)

    assert after == expected, find_issue(after, expected)
