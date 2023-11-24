from pydantic import BaseModel


class Order(BaseModel):
    id: int | None = None
    user_id: int
    item_id: int
    quantity: int
    process: int
    status: str

    class Config:
        from_attributes = True


class Item(BaseModel):
    id: int | None = None
    name: str
    price: int
    quantity: int
    orders: list[Order] = []

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int | None = None
    username: str
    credit: int
    orders: list[Order] = []

    class Config:
        from_attributes = True
