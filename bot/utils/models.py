from dataclasses import dataclass
from datetime import datetime
# from pydantic import BaseModel


# @dataclass(frozen=True, kw_only=True)
class Product:
    product_name: str
    price: float
    count: int | None


