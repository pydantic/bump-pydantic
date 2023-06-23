# Bump Pydantic ♻️

[![PyPI - Version](https://img.shields.io/pypi/v/bump-pydantic.svg)](https://pypi.org/project/bump-pydantic)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bump-pydantic.svg)](https://pypi.org/project/bump-pydantic)
[![PyPI - License](https://img.shields.io/pypi/l/bump-pydantic.svg)](https://pypi.org/project/bump-pydantic)


Bump Pydantic is a tool to help you migrate your code from Pydantic V1 to V2.


> **Note**
> If you find bugs, please report them on the [issue tracker](https://github.com/pydantic/bump-pydantic/issues/new).

---

## Installation

The installation is as simple as:

```bash
pip install bump-pydantic
```

---

## Usage

`bump-pydantic` is a CLI tool, hence you can use it from your terminal.

To see the available options, you can run:

```bash
bump-pydantic --help
```

### Check diff before applying changes

To check the diff before applying the changes, you can run:

```bash
bump-pydantic --diff <package>
```

### Apply changes

To apply the changes, you can run:

```bash
bump-pydantic <package>
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

### BP003: Replace `Config` class by `model_config`

- ✅ Replace `Config` class by `model_config = ConfigDict()`.

The following code will be transformed:

```py
class User(BaseModel):
    name: str

    class Config:
        extra = 'forbid'
```

Into:

```py
class User(BaseModel):
    name: str

    model_config = ConfigDict(extra='forbid')
```

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

T = TypeVar('T')

class User(BaseModel, Generic[T]):
    name: str
```

### BP006: Replace `__root__` by `RootModel`

To be implemented.

---

## License

This project is licensed under the terms of the MIT license.
