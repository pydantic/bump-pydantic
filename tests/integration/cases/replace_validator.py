from ..case import Case
from ..file import File

cases = [
    Case(
        name="Replace validator",
        source=File(
            "replace_validator.py",
            content=[
                "from pydantic import BaseModel, validator, root_validator",
                "",
                "",
                "class A(BaseModel):",
                "    a: int",
                "    b: str",
                "",
                "    @validator('a')",
                "    def validate_a(cls, v):",
                "        return v + 1",
                "",
                "    @root_validator()",
                "    def validate_b(cls, values):",
                "        return values",
            ],
        ),
        expected=File(
            "replace_validator.py",
            content=[
                "from pydantic import field_validator, model_validator, BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    a: int",
                "    b: str",
                "",
                "    @field_validator('a')",
                "    @classmethod",
                "    def validate_a(cls, v):",
                "        return v + 1",
                "",
                "    @model_validator()",
                "    @classmethod",
                "    def validate_b(cls, values):",
                "        return values",
            ],
        ),
    ),
    Case(
        name="Replace validator with existing classmethod decorator",
        source=File(
            "replace_validator_existing_classmethod.py",
            content=[
                "from pydantic import BaseModel, validator, root_validator",
                "",
                "",
                "class A(BaseModel):",
                "    a: int",
                "    b: str",
                "",
                "    @validator('a')",
                "    @classmethod",
                "    def validate_a(cls, v):",
                "        return v + 1",
                "",
                "    @root_validator()",
                "    @classmethod",
                "    def validate_b(cls, values):",
                "        return values",
            ],
        ),
        expected=File(
            "replace_validator_existing_classmethod.py",
            content=[
                "from pydantic import field_validator, model_validator, BaseModel",
                "",
                "",
                "class A(BaseModel):",
                "    a: int",
                "    b: str",
                "",
                "    @field_validator('a')",
                "    @classmethod",
                "    def validate_a(cls, v):",
                "        return v + 1",
                "",
                "    @model_validator()",
                "    @classmethod",
                "    def validate_b(cls, values):",
                "        return values",
            ],
        ),
    ),
    Case(
        name="Replace validator with pre=True",
        source=File(
            "const_to_literal.py",
            content=[
                "from enum import Enum",
                "from pydantic import BaseModel, Field",
                "",
                "",
                "class A(str, Enum):",
                "    a = 'a'",
                "    b = 'b'",
                "",
                "class A(BaseModel):",
                "    a: A = Field(A.a, const=True)",
            ],
        ),
        expected=File(
            "const_to_literal.py",
            content=[
                "from enum import Enum",
                "from pydantic import BaseModel",
                "from typing import Literal",
                "",
                "",
                "class A(str, Enum):",
                "    a = 'a'",
                "    b = 'b'",
                "",
                "class A(BaseModel):",
                "    a: Literal[A.a] = A.a",
            ],
        ),
    ),
]
