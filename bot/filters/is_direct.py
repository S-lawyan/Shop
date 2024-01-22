from typing import Union

from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, InlineQuery, ChatType
from aiogram.dispatcher.filters import BoundFilter


class IsDirect(BoundFilter):
    async def check(self, obj: Union[Message, CallbackQuery, ChatMemberUpdated, InlineQuery]):
        if isinstance(obj, CallbackQuery):
            chat_type = obj.message.chat.type if obj.message else None
        else:
            chat_type = obj.chat.type
        return chat_type in [ChatType.PRIVATE]
