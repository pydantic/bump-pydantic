from typing import Any, Dict, Optional, Union

from pydantic import BaseModel


class A(BaseModel):
    a: int | None
    b: Optional[int]
    c: Union[int, None]
    d: Any
    e: Dict[str, str]
