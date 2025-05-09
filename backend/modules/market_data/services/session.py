import json
import asyncio
import datetime

from backend.cache import SessionCache
from backend.common.consts import SQLServerConsts
# from backend.modules.market_data.entities import OHLC
# from backend.modules.market_data.repositories import OHLCRepo
from backend.modules.market_data.dnse_service import DNSEService
from backend.modules.market_data.configs import Topics
from backend.utils.logger import LOGGER


class SessionService(DNSEService):
    topic = Topics.SESSION
    # repo = OHLCRepo

    @classmethod
    async def handle_msg(cls, client, userdata, msg):
        try:
            session_payload = json.loads(msg.payload.decode())

            if session_payload.get("floorCode"):
                LOGGER.info(f"Received message: {session_payload}")
                await SessionCache.add(session=session_payload)

        except Exception as e:
            raise Exception(f"Failed to decode message: {e}")
