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
