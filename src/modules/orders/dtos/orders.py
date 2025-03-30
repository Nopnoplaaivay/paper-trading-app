from src.modules.base.dto import BaseDTO


class OrdersDTO(BaseDTO):
    symbol: str
    side: str
    price: int
    order_type: str = "MP"
    order_quantity: int
    account_id: str
