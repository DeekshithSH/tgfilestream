# tgfs - A Telegram bot that can stream Telegram files to users over HTTP.
# Copyright (C) 2019 Tulir Asokan
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

# Modifications made by Deekshith SH, 2025
# Copyright (C) 2025 Deekshith SH
from typing import Dict, Optional, cast
from collections import defaultdict
import logging

from telethon.tl.custom import Message
from aiohttp import web

from .cache_util import FileInfo, lru_cache
from .util import unpack_id, get_file_name, get_requester_ip
from .config import request_limit, cache_size
from .telegram import client, transfer

log = logging.getLogger(__name__)
routes = web.RouteTableDef()
ongoing_requests: Dict[str, int] = defaultdict(lambda: 0)

@routes.get("/")
async def handle_root_request(_) -> web.Response:
    return web.json_response({
        "status": "ok",
        "source": "https://github.com/DeekshithSH/tgfs"
    })

@routes.head(r"/{id:[0-9a-fA-F]+}/{name}")
async def handle_head_request(req: web.Request) -> web.Response:
    return await handle_request(req, head=True)


@routes.get(r"/{id:[0-9a-fA-F]+}/{name}", allow_head=False)
async def handle_get_request(req: web.Request) -> web.Response:
    return await handle_request(req, head=False)


def allow_request(ip: str) -> None:
    return ongoing_requests[ip] < request_limit


def increment_counter(ip: str) -> None:
    ongoing_requests[ip] += 1


def decrement_counter(ip: str) -> None:
    ongoing_requests[ip] -= 1

@lru_cache(cache_size, True)
async def get_file(file_id: int, expected_name: str) -> Optional[FileInfo]:
    peer, msg_id = unpack_id(file_id)
    if not peer or not msg_id:
        return None
    message = cast(Message, await client.get_messages(entity=peer, ids=msg_id))
    if not message or not message.file or get_file_name(message) != expected_name:
        return None
    return FileInfo(message)

async def handle_request(req: web.Request, head: bool = False) -> web.Response:
    file_name = req.match_info["name"]
    file_id = int(req.match_info["id"], 16)

    file = await get_file(file_id, file_name)
    if not file:
        return web.Response(status=404, text="404: Not Found")

    size = file.size
    try:
        range_header = req.headers.get("Range", 0)
        if range_header:
            offset, until_bytes = range_header.replace("bytes=", "").split("-")
            offset = int(offset)
            limit = int(until_bytes) if until_bytes else size - 1
        else:
            offset = req.http_range.start or 0
            limit = (req.http_range.stop or size) - 1

        if (limit >= size) or (offset < 0) or (limit < offset):
            raise ValueError("range not in acceptable format")
    except ValueError:
        return web.Response(status=416, text="416: Range Not Satisfiable",
                            headers={"Content-Range": f"bytes */{size}"})
    if not head:
        ip = get_requester_ip(req)
        if not allow_request(ip):
            return web.Response(status=429)
        log.info(f"Serving file in {file.msg_id} (chat {file.chat_id}) to {ip}; Range: {offset} - {limit}")
        body = transfer.download(file.location, file.dc_id, file_size=size, offset=offset, limit=limit)
    else:
        body = None
    return web.Response(status=200 if (offset == 0 and limit == size - 1) else 206,
                        body=body,
                        headers={
                            "Content-Type": file.mime_type,
                            "Content-Range": f"bytes {offset}-{limit}/{size}",
                            "Content-Length": str(limit - offset + 1),
                            "Content-Disposition": f'attachment; filename="{file_name}"',
                            "Accept-Ranges": "bytes",
                        })
