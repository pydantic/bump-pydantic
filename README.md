# Bump Pydantic ♻️

[![PyPI - Version](https://img.shields.io/pypi/v/bump-pydantic.svg)](https://pypi.org/project/bump-pydantic)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bump-pydantic.svg)](https://pypi.org/project/bump-pydantic)


Bump Pydantic is a tool to help you migrate your code from Pydantic V1 to V2.


> [!NOTE]\
> If you find bugs, please report them on the [issue tracker](https://github.com/pydantic/bump-pydantic/issues/new).

## Table of contents

- [Bump Pydantic ♻️](#bump-pydantic-️)
  - [Table of contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Check diff before applying changes](#check-diff-before-applying-changes)
    - [Apply changes](#apply-changes)
  - [Rules](#rules)
    - [BP001: Add default `None` to `Optional[T]`, `Union[T, None]` and `Any` fields](#bp001-add-default-none-to-optionalt-uniont-none-and-any-fields)
    - [BP002: Replace `Config` class by `model_config` attribute](#bp002-replace-config-class-by-model_config-attribute)
    - [BP003: Replace `Field` old parameters to new ones](#bp003-replace-field-old-parameters-to-new-ones)
    - [BP004: Replace imports](#bp004-replace-imports)
    - [BP005: Replace `GenericModel` by `BaseModel`](#bp005-replace-genericmodel-by-basemodel)
    - [BP006: Replace `__root__` by `RootModel`](#bp006-replace-__root__-by-rootmodel)
    - [BP007: Replace decorators](#bp007-replace-decorators)
    - [BP008: Replace `con*` functions by `Annotated` versions](#bp008-replace-con-functions-by-annotated-versions)
  - [License](#license)

---

## Installation

The installation is as simple as:

```bash
pip install bump-pydantic
```

---

## Usage

`bump-pydantic` is a CLI tool, hence you can use it from your terminal.

It's easy to use. If your project structure is:

```bash
repository/
└── my_package/
    └── <python source files>
```

Then you'll want to do:

```bash
cd /path/to/repository
bump-pydantic my_package
```

### Check diff before applying changes

To check the diff before applying the changes, you can run:

```bash
bump-pydantic --diff <path>
```

### Apply changes

To apply the changes, you can run:

```bash
bump-pydantic <path>
```

## Rules

You can find below the list of rules that are applied by `bump-pydantic`.

It's also possible to disable rules by using the `--disable` option.

### BP001: Add default `None` to `Optional[T]`, `Union[T, None]` and `Any` fields

- ✅ Add default `None` to `Optional[T]` fields.

The following code will be transformed:

```py
class User(BaseModel):
    name: Optional[str]
```

Into:

```py
class User(BaseModel):
    name: Optional[str] = None
```

### BP002: Replace `Config` class by `model_config` attribute

- ✅ Replace `Config` class by `model_config = ConfigDict()`.
- ✅ Rename old `Config` attributes to new `model_config` attributes.
- ✅ Add a TODO comment in case the transformation can't be done automatically.
- ✅ Replace `Extra` enum by string values.

The following code will be transformed:

```py
from pydantic import BaseModel, Extra


class User(BaseModel):
    name: str

    class Config:
        extra = Extra.forbid
```

Into:

```py
from pydantic import ConfigDict, BaseModel


class User(BaseModel):
    name: str

    model_config = ConfigDict(extra="forbid")
```

### BP003: Replace `Field` old parameters to new ones

- ✅ Replace `Field` old parameters to new ones.
- ✅ Replace `field: Enum = Field(Enum.VALUE, const=True)` by `field: Literal[Enum.VALUE] = Enum.VALUE`.

The following code will be transformed:

```py
from typing import List

from pydantic import BaseModel, Field


class User(BaseModel):
    name: List[str] = Field(..., min_items=1)
```

Into:

```py
from typing import List

from pydantic import BaseModel, Field


class User(BaseModel):
    name: List[str] = Field(..., min_length=1)
```

### BP004: Replace imports

- ✅ Replace `BaseSettings` from `pydantic` to `pydantic_settings`.
- ✅ Replace `Color` and `PaymentCardNumber` from `pydantic` to `pydantic_extra_types`.

### BP005: Replace `GenericModel` by `BaseModel`

- ✅ Replace `GenericModel` by `BaseModel`.

The following code will be transformed:

```py
from typing import Generic, TypeVar
from pydantic.generics import GenericModel

T = TypeVar('T')

class User(GenericModel, Generic[T]):
    name: str
```

Into:

```py
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class User(BaseModel, Generic[T]):
    name: str
```

### BP006: Replace `__root__` by `RootModel`

- ✅ Replace `__root__` by `RootModel`.

The following code will be transformed:

```py
from typing import List

from pydantic import BaseModel

class User(BaseModel):
    age: int
    name: str

class Users(BaseModel):
    __root__ = List[User]
```

Into:

```py
from typing import List

from pydantic import RootModel, BaseModel

class User(BaseModel):
    age: int
    name: str

class Users(RootModel[List[User]]):
    pass
```

### BP007: Replace decorators

- ✅ Replace `@validator` by `@field_validator`.
- ✅ Replace `@root_validator` by `@model_validator`.

The following code will be transformed:

```py
from pydantic import BaseModel, validator, root_validator


class User(BaseModel):
    name: str

    @validator('name', pre=True)
    def validate_name(cls, v):
        return v

    @root_validator(pre=True)
    def validate_root(cls, values):
        return values
```

Into:

```py
from pydantic import BaseModel, field_validator, model_validator


class User(BaseModel):
    name: str

    @field_validator('name', mode='before')
    def validate_name(cls, v):
        return v

    @model_validator(mode='before')
    def validate_root(cls, values):
        return values
```

### BP008: Replace `con*` functions by `Annotated` versions

- ✅ Replace `constr(*args)` by `Annotated[str, StringConstraints(*args)]`.
- ✅ Replace `conint(*args)` by `Annotated[int, Field(*args)]`.
- ✅ Replace `confloat(*args)` by `Annotated[float, Field(*args)]`.
- ✅ Replace `conbytes(*args)` by `Annotated[bytes, Field(*args)]`.
- ✅ Replace `condecimal(*args)` by `Annotated[Decimal, Field(*args)]`.
- ✅ Replace `conset(T, *args)` by `Annotated[Set[T], Field(*args)]`.
- ✅ Replace `confrozenset(T, *args)` by `Annotated[Set[T], Field(*args)]`.
- ✅ Replace `conlist(T, *args)` by `Annotated[List[T], Field(*args)]`.

The following code will be transformed:

```py
from pydantic import BaseModel, constr


class User(BaseModel):
    name: constr(min_length=1)
```

Into:

```py
from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated


class User(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
```

<!-- ### BP009: Replace `pydantic.parse_obj_as` by `pydantic.TypeAdapter`

- ✅ Replace `pydantic.parse_obj_as(T, obj)` to `pydantic.TypeAdapter(T).validate_python(obj)`.


The following code will be transformed:

```py
from typing import List

from pydantic import BaseModel, parse_obj_as


class User(BaseModel):
    name: str


class Users(BaseModel):
    users: List[User]


users = parse_obj_as(Users, {'users': [{'name': 'John'}]})
```

Into:

```py
from typing import List

from pydantic import BaseModel, TypeAdapter


class User(BaseModel):
    name: str


class Users(BaseModel):
    users: List[User]


users = TypeAdapter(Users).validate_python({'users': [{'name': 'John'}]})
``` -->

<!-- ### BP010: Replace `PyObject` by `ImportString`

- ✅ Replace `PyObject` by `ImportString`.

The following code will be transformed:

```py
from pydantic import BaseModel, PyObject


class User(BaseModel):
    name: PyObject
```

Into:

```py
from pydantic import BaseModel, ImportString


class User(BaseModel):
    name: ImportString
``` -->

---

## License

This project is licensed under the terms of the MIT license.
