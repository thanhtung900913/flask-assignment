from pydantic import BaseModel

class FavouriteClassDTO(BaseModel):
    user_id: str
    class_id: str
    