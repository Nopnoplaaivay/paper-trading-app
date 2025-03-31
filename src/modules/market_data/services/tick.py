import json
import asyncio
import datetime

from src.modules.market_data.entities import Tick
from src.modules.market_data.repositories import TickRepo
from src.modules.market_data.dnse_service import DNSEService
from src.modules.market_data.configs import Topics
from src.utils.logger import LOGGER

class TickService(DNSEService):
    topic = Topics.TICK
    repo = TickRepo

    @classmethod
    def on_message(cls, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            LOGGER.info(f"Received message: {data}")

            if data.get("time") is None:
                return

            trading_time = datetime.datetime.fromisoformat(
                data.get("time").replace("Z", "+00:00")
            ) 
            coroutine = cls.repo.insert(
                record={
                    Tick.symbol.name: data.get("symbol"),
                    Tick.trading_time.name: trading_time,
                    Tick.match_price.name: data.get("matchPrice"),
                    Tick.match_quantity.name: data.get("matchQtty"),
                    Tick.session.name: data.get("session"),
                },
                returning=False
            )
            asyncio.run_coroutine_threadsafe(coroutine, cls.loop)

        except Exception as e:
            raise Exception(f"Failed to decode message: {e}")
