from src.modules.base.dto import BaseDTO

class RegisterDTO(BaseDTO):
    account: str
    password: str
    confirm_password: str
    role: str
    type_broker: str
    type_client: str

class LoginDTO(BaseDTO):
    account: str
    password: str