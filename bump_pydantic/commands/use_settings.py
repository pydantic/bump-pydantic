from libcst.codemod import CodemodContext
from libcst.codemod.commands.rename import RenameCommand


def UsePydanticSettingsCommand(context: CodemodContext):
    """Support for pydantic.BaseSettings.

    This command will rename pydantic.BaseSettings to pydantic_settings:BaseSettings.

    It doesn't support the following cases:
    - from pydantic.settings import BaseSettings
    - import pydantic ... class Settings(pydantic.BaseSettings)
    - import pydantic as pd ... class Settings(pd.BaseSettings)

    TODO: Support the above cases. To implement the above, you'll need to go to each
    `ClassDef`, and see the bases. If there's a `pydantic.settings.BaseSettings` in the
    bases, then you'll need to use `RemoveImportsVisitor` and `AddImportsVisitor` from
    `libcst.codemod.visitors`.
    """
    return RenameCommand(
        context=context,
        old_name="pydantic.BaseSettings",
        new_name="pydantic_settings:BaseSettings",
    )
