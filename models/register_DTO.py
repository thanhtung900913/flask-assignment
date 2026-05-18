from pydantic import BaseModel

class RegisterDTO(BaseModel):
    username: str
    password: str
