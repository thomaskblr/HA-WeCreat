"""Local, read-only access to the WeCreat process status."""
import asyncio
from ipaddress import ip_address
import re

from aiohttp import ClientError, ClientSession, ClientTimeout
from yarl import URL

LABELS = {2: "running", 3: "cooldown", 4: "ready"}


def normalize_host(value):
    host = value.strip().lower()
    try:
        return str(ip_address(host))
    except ValueError:
        labels = host.rstrip(".").split(".")
        if len(host) > 253 or not all(
            re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
            for label in labels
        ):
            raise ValueError("Enter an IP address or hostname")
        return ".".join(labels)


class StatusError(Exception):
    """The laser did not return a usable status."""


async def read_status(session: ClientSession, host: str, port: int) -> int:
    url = URL.build(scheme="http", host=host, port=port, path="/process/status")
    try:
        async with session.post(url, timeout=ClientTimeout(total=4),
                                allow_redirects=False) as response:
            if response.status != 200:
                raise StatusError(f"Laser returned HTTP {response.status}")
            data = await response.json(content_type=None)
    except (ClientError, asyncio.TimeoutError, ValueError) as err:
        raise StatusError("Cannot read laser status") from err
    if not isinstance(data, dict) or data.get("code") != 0 or type(data.get("status")) is not int:
        raise StatusError("Unexpected laser response")
    return data["status"]


class PhotoError(Exception):
    """The laser did not return a complete bed photograph."""


async def read_photo(session: ClientSession, host: str, port: int) -> bytes:
    url = URL.build(scheme="http", host=host, port=port, path="/camera/take_photo")
    try:
        async with session.get(url, timeout=ClientTimeout(total=15),
                               allow_redirects=False) as response:
            if response.status != 200:
                raise PhotoError(f"Camera returned HTTP {response.status}")
            image = bytearray()
            async for chunk in response.content.iter_chunked(65536):
                image.extend(chunk)
                if len(image) > 16 * 1024 * 1024:
                    raise PhotoError("Camera response exceeds 16 MiB")
    except (ClientError, asyncio.TimeoutError) as err:
        raise PhotoError("Cannot reach the bed camera") from err
    if not image.startswith(b"\xff\xd8\xff") or not image.endswith(b"\xff\xd9"):
        raise PhotoError("Camera returned an incomplete or invalid JPEG")
    return bytes(image)
