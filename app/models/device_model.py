from pydantic import BaseModel

class DeviceRequestBody(BaseModel):
    device_info: str
    is_disabled: bool