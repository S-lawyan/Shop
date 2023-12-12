from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


@dataclass(kw_only=True)
class Product:
    product_name: str
    price: float
    quantity: int | None
    article: int
    trader_id: int
