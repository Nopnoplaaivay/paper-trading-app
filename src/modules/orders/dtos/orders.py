from src.modules.base.dto import BaseDTO


class OrdersDTO(BaseDTO):
    symbol: str
    side: str
    price: int = 0
    order_type: str = "MP"
    qtty: int
    account_id: str

class OrdersCancelDTO(BaseDTO):
    order_id: str
    account_id: str

class OrdersResponseDTO(BaseDTO):
    id: str
    side: str
    symbol: str
    price: int
    qtty: int
    order_type: str = "MP"
    status: str = "PENDING"