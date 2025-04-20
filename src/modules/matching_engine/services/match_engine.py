import time

from src.cache.shared_state import STOP_EVENT
from src.modules.dnse.realtime_data_provider import RealtimeDataProvider
from src.modules.orders.processors import OrdersProcessors
from src.modules.orders.repositories import OrdersRepo
from src.modules.orders.entities import Orders
from src.utils.logger import LOGGER


INTERVAL_SECONDS = 3


class MatchEngineService:
    @classmethod
    async def get_pending_orders(cls) -> list[Orders]:
        try:
            conditions = {Orders.status.name: "PENDING"}
            pending_orders = await OrdersRepo.get_by_condition(conditions=conditions)
            if pending_orders:
                 LOGGER.debug(f"Found {len(pending_orders)} pending limit orders to check.")
            return pending_orders
        except Exception as e:
            LOGGER.error(f"Error fetching pending limit orders from DB: {e}", exc_info=True)
            return []

    @classmethod
    async def check_matches(cls):
        LOGGER.debug("Running limit order check cycle...")
        pending_orders = await cls.get_pending_orders()
        if not pending_orders:
            LOGGER.debug("No pending limit orders found in this cycle.")
            return

        for order in pending_orders:
            if STOP_EVENT.is_set():
                LOGGER.info("Stop event received during order checking. Aborting cycle.")
                return
            try:
                current_price = RealtimeDataProvider.get_market_price(order["symbol"])
                if current_price is None:
                    LOGGER.warning(f"No market price available for {order['symbol']}. Skipping order {order['id']}.")
                    continue

                if order["order_type"] == "MP":
                    order["price"] = current_price
                    await OrdersProcessors.update_on_complete(order=order)
                elif order["order_type"] == "LO":
                    if current_price == order["price"]:
                        await OrdersProcessors.update_on_complete(order=order)

            except Exception as check_err:
                LOGGER.error(f"Error checking individual order {order['id']}: {check_err}", exc_info=True)

    @classmethod
    async def run(cls):
        """Main loop for the matcher worker, calling check_and_queue_matches periodically."""
        LOGGER.info("LimitOrderMatcherWorker thread started.")
        while not STOP_EVENT.is_set():
            try:
                LOGGER.info("Checking pending orders...")
                await cls.check_matches()
                time.sleep(INTERVAL_SECONDS)
            except Exception as loop_err:
                LOGGER.error(f"Error in worker loop: {loop_err}", exc_info=True)
                time.sleep(5)
