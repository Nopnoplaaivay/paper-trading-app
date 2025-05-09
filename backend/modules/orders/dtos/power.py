from backend.modules.base.dto import BaseDTO


class PowerDTO(BaseDTO):
    account_id: str
    symbol: str
    price: int


class PowerResponseDTO(BaseDTO):
    account_id: str
    ppse: int
    pp_total: int
    qmax: int
    qmax_long: int
    qmax_short: int
    trade_quantity: int
    price: int