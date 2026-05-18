from pydantic import BaseModel

class LoginDTO(BaseModel):
    username: str
    password: str
    device_info: str
    device_id: str