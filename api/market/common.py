from typing import Any

import httpx

from ayon_server.addons import AddonLibrary
from ayon_server.config import ayonconfig
from ayon_server.exceptions import ForbiddenException
from ayon_server.helpers.cloud import get_cloud_api_headers
from ayon_server.lib.postgres import Postgres


async def get_market_data(
    *args: str,
) -> dict[str, Any]:
    """Get data from the market API"""

    endpoint = "/".join(args)

    headers = await get_cloud_api_headers()

    if not headers:
        raise ForbiddenException("Ayon is not connected to Ynput Cloud [ERR 2]")

    async with httpx.AsyncClient(timeout=ayonconfig.http_timeout) as client:
        res = await client.get(
            f"{ayonconfig.ynput_cloud_api_url}/api/v1/market/{endpoint}",
            headers=headers,
        )

    if res.status_code == 401:
        raise ForbiddenException("Unauthorized instance")

    res.raise_for_status()  # should not happen

    return res.json()


async def get_local_latest_addon_versions() -> dict[str, str]:
    """Get the current latest versions of installed addons

    Used to check if there are new versions available
    """

    return AddonLibrary.get_addons_latest_versions()



async def get_local_production_addon_versions() -> dict[str, str]:
    """Get the current production versions of installed addons

    Used to check if there are new versions available
    """

    res = await Postgres.fetch(
        "SELECT data->'addons' as addons FROM bundles WHERE is_production"
    )
    if not res:
        return {}

    return res[0]["addons"] or {}
