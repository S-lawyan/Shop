from aiogram import Dispatcher
from .is_chat import IsGroup
from .is_direct import IsDirect


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsGroup,
                            event_handlers=[dp.message_handlers, dp.callback_query_handlers, dp.inline_query_handlers])
    dp.filters_factory.bind(IsDirect,
                            event_handlers=[dp.message_handlers, dp.callback_query_handlers, dp.inline_query_handlers])
