from pydantic import BaseModel


class Order(BaseModel):
    id: int | None = None
    user: str
    item: str
    price: str
    status: str

    class Config:
        from_attributes = True
