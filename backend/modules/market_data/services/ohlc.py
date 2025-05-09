import json
import asyncio
import datetime

from backend.cache import OHLCCache
from backend.common.consts import SQLServerConsts
from backend.modules.market_data.entities import OHLC
from backend.modules.market_data.repositories import OHLCRepo
from backend.modules.market_data.dnse_service import DNSEService
from backend.modules.market_data.configs import Topics
from backend.utils.logger import LOGGER


class OHLCService(DNSEService):
    topic = Topics.OHLC_1M
    repo = OHLCRepo

    @classmethod
    async def handle_msg(cls, client, userdata, msg):
        try:
            ohlc_payload = json.loads(msg.payload.decode())
            LOGGER.info(f"Received message: {ohlc_payload}")

            if ohlc_payload.get("close"):
                await OHLCCache.add(ohlc=ohlc_payload)


        except Exception as e:
            raise Exception(f"Failed to decode message: {e}")
