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
