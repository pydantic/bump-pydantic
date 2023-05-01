# bump-pydantic

[![PyPI - Version](https://img.shields.io/pypi/v/bump-pydantic.svg)](https://pypi.org/project/bump-pydantic)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bump-pydantic.svg)](https://pypi.org/project/bump-pydantic)

-----

**Table of Contents**

- [bump-pydantic](#bump-pydantic)
  - [Installation](#installation)
  - [Checklist](#checklist)
  - [License](#license)

## Installation

```console
pip install bump-pydantic
```

## Checklist

- [X] `Config` class to `model_config` attribute on `BaseModel`.
- [ ] Removed Constrained<Type>" - raise warning.
- [X] Replace imports that changed location.
- [ ] Add None as default value to `Optional[X]`, and `Any`. Unless it has `...` as default value.
- [ ] `min_items` becomes `min_length`.

## License

`bump-pydantic` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
