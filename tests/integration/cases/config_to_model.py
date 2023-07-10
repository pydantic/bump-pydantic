import textwrap

from ..case import Case
from ..file import File

cases = [
    Case(
        id="Replace Config class to model",
        input=File(
            "config_to_model.py",
            content=textwrap.dedent("""\
                from pydantic import BaseModel
                
                
                class A(BaseModel):
                    class Config:
                        orm_mode = True
                        validate_all = True
                
                
                class BaseConfig:
                    orm_mode = True
                    validate_all = True
                
                
                class B(BaseModel):
                    class Config(BaseConfig):
                        ...
            """).splitlines(),
        ),
        expected=File(
            "config_to_model.py",
            content=textwrap.dedent("""\
                from pydantic import ConfigDict, BaseModel
                
                
                class A(BaseModel):
                    model_config = ConfigDict(from_attributes=True, validate_default=True)
                
                
                class BaseConfig:
                    orm_mode = True
                    validate_all = True
                
                
                class B(BaseModel):
                    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
                    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
                    class Config(BaseConfig):
                        ...",
            """).splitlines(),
        ),
    ),
    Case(
        id="Replace Config class on BaseSettings",
        input=File(
            "config_dict_and_settings.py",
            content=textwrap.dedent("""\
                from pydantic import BaseModel, BaseSettings
                
                
                class Settings(BaseSettings):
                    sentry_dsn: str
                
                    class Config:
                        orm_mode = True
                
                
                class A(BaseModel):
                    class Config:
                        orm_mode = True
            """).splitlines(),
        ),
        expected=File(
            "config_dict_and_settings.py",
            content=textwrap.dedent("""\
                from pydantic import ConfigDict, BaseModel
                from pydantic_settings import BaseSettings, SettingsConfigDict
                
                
                class Settings(BaseSettings):
                    sentry_dsn: str
                    model_config = SettingsConfigDict(from_attributes=True)
                
                
                class A(BaseModel):
                    model_config = ConfigDict(from_attributes=True)
            """).splitlines(),
        ),
    ),
]
