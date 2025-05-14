# tgfs - A Telegram bot that can stream Telegram files to users over HTTP.
# Copyright (C) 2025 Deekshith SH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import asyncio
import logging

from collections import OrderedDict
from typing import Optional, Callable, Awaitable, Any

from telethon.utils import get_input_location
from telethon.tl.custom import Message

from .paralleltransfer import TypeLocation

log = logging.getLogger(__name__)


class AsyncLRUCache:
    def __init__(self, fn: Callable[..., Awaitable[Any]], maxsize: Optional[int], use_first_arg: bool):
        self.fn = fn
        self.maxsize = maxsize
        self.use_first_arg = use_first_arg
        self.cache: OrderedDict[int, asyncio.Task] = OrderedDict()

    def _make_key(self, args, kwargs):
        if self.use_first_arg:
            if not args:
                raise ValueError("First argument missing for use_first_arg=True")
            return hash(args[0])
        else:
            key_data = args
            if kwargs:
                key_data += tuple(sorted(kwargs.items()))
            return hash(key_data)

    async def __call__(self, *args, **kwargs):
        key = self._make_key(args, kwargs)

        if key in self.cache:
            task = self.cache[key]
            self.cache.move_to_end(key)
            return await asyncio.shield(task)

        async def call():
            try:
                return await self.fn(*args, **kwargs)
            except Exception:
                self.cache.pop(key, None)
                raise

        task = asyncio.create_task(call())
        self.cache[key] = task

        if self.maxsize is not None and len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)

        result = await asyncio.shield(task)
        if result is None:
            self.cache.pop(key, None)
        return result

    def cache_clear(self):
        self.cache.clear()

def lru_cache(maxsize: Optional[int] = 128, use_first_arg: bool = False):
    def decorator(fn: Callable[..., Awaitable[Any]]):
        return AsyncLRUCache(fn, maxsize, use_first_arg)
    return decorator

class FileInfo:
    __slots__ = ("size", "mime_type", "dc_id", "location", "msg_id", "chat_id")

    size: int
    mime_type: str
    dc_id: int
    location: TypeLocation
    msg_id: int
    chat_id: int

    def __init__(self, message: Message):
        self.size = message.file.size
        self.mime_type = message.file.mime_type
        self.dc_id, self.location = get_input_location(message.media)
        self.msg_id = message.id
        self.chat_id = message.chat_id
