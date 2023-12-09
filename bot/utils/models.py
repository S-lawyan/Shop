from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel


# @dataclass(frozen=True, kw_only=True)
@dataclass(kw_only=True)
class Trader(BaseModel):
    shop_name: str
    fio: str
    tg_id: int

