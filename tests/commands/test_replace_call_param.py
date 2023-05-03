from __future__ import annotations
import textwrap

from pathlib import Path

import libcst as cst
import pytest
from libcst.codemod import CodemodContext
from libcst.metadata import MetadataWrapper
from libcst_mypy import MypyTypeInferenceProvider

from bump_pydantic.commands.replace_call_param import ReplaceCallParam


@pytest.mark.parametrize(
    "source, output",
    [
        pytest.param(
            """
            from pydantic import ConfigDict

            ConfigDict(kwarg="potato")
            """,
            """
            from pydantic import ConfigDict

            ConfigDict(param="potato")
            """,
            id="simple",
        ),
        pytest.param(
            """
            from pydantic import ConfigDict as ConfigDicto

            ConfigDicto(kwarg="potato")
            """,
            """
            from pydantic import ConfigDict as ConfigDicto

            ConfigDicto(param="potato")
            """,
            id="alias",
        ),
        pytest.param(
            """
            from pydantic import config

            config.ConfigDict(kwarg="potato")
            """,
            """
            from pydantic import config

            config.ConfigDict(param="potato")
            """,
            id="from",
        ),
        pytest.param(
            """
            from pydantic import config as configo

            configo.ConfigDict(kwarg="potato")
            """,
            """
            from pydantic import config as configo

            configo.ConfigDict(param="potato")
            """,
            id="from_alias",
        ),
        pytest.param(
            """
            import pydantic

            pydantic.ConfigDict(kwarg="potato")
            """,
            """
            import pydantic

            pydantic.ConfigDict(param="potato")
            """,
            id="import",
        ),
    ],
)
def test_replace_call_param(source: str, output: str, tmp_path: Path) -> None:
    package = tmp_path / "package"
    package.mkdir()

    source_path = package / "a.py"
    source_path.write_text(textwrap.dedent(source))

    file = str(source_path)
    cache = MypyTypeInferenceProvider.gen_cache(package, [file])
    wrapper = MetadataWrapper(
        cst.parse_module(source_path.read_text()),
        cache={MypyTypeInferenceProvider: cache[file]},
    )
    module = wrapper.visit(
        ReplaceCallParam(
            context=CodemodContext(wrapper=wrapper),
            callers=("pydantic.config.ConfigDict", "pydantic.ConfigDict"),
            params={"kwarg": "param"},
        )
    )
    assert module.code == textwrap.dedent(output)
