import json
import asyncio
import datetime

from src.common.consts import SQLServerConsts
from src.modules.market_data.entities import StockInfo
from src.modules.market_data.repositories import StockInfoRepo
from src.modules.market_data.dnse_service import DNSEService
from src.modules.market_data.configs import Topics
from src.utils.logger import LOGGER


class StockInfoService(DNSEService):
    topic = Topics.STOCK_INFO
    repo = StockInfoRepo

    @classmethod
    def proccess_msg(cls, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            LOGGER.info(f"Received message: {data}")

            if data.get("tradingTime") is None or data.get("securityType") != "STOCK":
                return

            trading_time = datetime.datetime.fromisoformat(
                data.get("tradingTime").replace("Z", "+00:00")
            )
            coroutine = cls.repo.insert(
                record={
                    StockInfo.floor_code.name: data.get("floorCode"),
                    StockInfo.symbol.name: data.get("symbol"),
                    StockInfo.trading_time.name: datetime.datetime.fromisoformat(
                        data.get("tradingTime").replace("Z", "+00:00")
                    ).strftime(SQLServerConsts.TRADING_TIME_FORMAT),
                    StockInfo.security_type.name: data.get("securityType"),
                    StockInfo.ceiling_price.name: data.get("ceilingPrice"),
                    StockInfo.floor_price.name: data.get("floorPrice"),
                    StockInfo.highest_price.name: data.get("highestPrice"),
                    StockInfo.lowest_price.name: data.get("lowestPrice"),
                    StockInfo.avg_price.name: data.get("avgPrice"),
                    StockInfo.buy_foreign_quantity.name: data.get("buyForeignQtty"),
                    StockInfo.sell_foreign_quantity.name: data.get("sellForeignQtty"),
                    StockInfo.current_room.name: data.get("currentRoom"),
                    StockInfo.accumulated_value.name: data.get("accumulatedVal"),
                    StockInfo.accumulated_volume.name: data.get("accumulatedVol"),
                    StockInfo.match_price.name: data.get("matchPrice"),
                    StockInfo.match_quantity.name: data.get("matchQtty"),
                    StockInfo.changed.name: data.get("changed"),
                    StockInfo.changed_ratio.name: data.get("changedRatio"),
                    StockInfo.estimated_price.name: data.get("estimatedPrice"),
                    StockInfo.trading_session.name: data.get("tradingSession"),
                    StockInfo.security_status.name: data.get("securityStatus"),
                    StockInfo.odd_lot_security_status.name: data.get(
                        "oddLotSecurityStatus"
                    ),
                },
                returning=False,
            )

            asyncio.run_coroutine_threadsafe(coroutine, cls.loop)

        except Exception as e:
            raise Exception(f"Failed to decode message: {e}")
