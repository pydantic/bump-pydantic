# Bump Pydantic ♻️

<!-- [![PyPI - Version](https://img.shields.io/pypi/v/bump-pydantic.svg)](https://pypi.org/project/bump-pydantic)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bump-pydantic.svg)](https://pypi.org/project/bump-pydantic) -->

Utility to bump pydantic from V1 to V2.

-----

### Rules

#### BP001: Replace imports

- ✅ Replace `BaseSettings` from `pydantic` to `pydantic_settings`.
- ✅ Replace `Color` and `PaymentCardNumber` from `pydantic` to `pydantic_extra_types`.

#### BP003: Replace `BaseModel` methods

#### BP002: Replace `Config` class by `model_config`
