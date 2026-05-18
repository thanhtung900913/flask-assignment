from pydantic import BaseModel

class DeviceDTO(BaseModel):
    device_info: str
    is_disabled: bool