from backend.modules.base.dto import BaseDTO


class UpdateUserRoleDTO(BaseDTO):
    user_id: int
    role: str

class AdminCancelOrdersDTO(BaseDTO):
    order_id: str