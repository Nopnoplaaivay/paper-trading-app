from src.modules.base.dto import BaseDTO


class DepositDTO(BaseDTO):
    account_id: str
    amount: int
    payment_method: str

class WithdrawDTO(BaseDTO):
    account_id: str
    amount: int
    payment_method: str