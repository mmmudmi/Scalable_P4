from pydantic import BaseModel


class Order(BaseModel):
    id: int | None
    user_id: int
    item_id: int
    quantity: int
    process: int
    status: str

    class Config:
        orm_mode = True


class Item(BaseModel):
    id: int | None
    name: str
    price: int
    quantity: int
    orders: list[Order] = []

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int | None
    username: str
    credit: int
    orders: list[Order] = []

    class Config:
        orm_mode = True
