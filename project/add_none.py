from pydantic import BaseModel
from typing import Optional, Union, Any


class A(BaseModel):
    a: int | None
    b: Optional[int]
    c: Union[int, None]
    d: Any
