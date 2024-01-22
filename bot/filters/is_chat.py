from typing import Union

from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, InlineQuery, ChatType
from aiogram.dispatcher.filters import BoundFilter


class IsGroup(BoundFilter):
    async def check(self, obj: Union[Message, CallbackQuery, ChatMemberUpdated, InlineQuery]):
        return obj.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]
    