from pydantic import BaseModel

class FavouriteClassRequestBody(BaseModel):
    user_id: str
    class_id: str
    