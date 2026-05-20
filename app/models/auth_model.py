from pydantic import BaseModel

class RegisterRequestBody(BaseModel):
    username: str
    password: str

class LoginRequestBody(BaseModel):
    username: str
    password: str
    device_info: str
    device_id: str