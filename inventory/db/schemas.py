from pydantic import BaseModel


class AbstractBase(BaseModel):
    id: int | None = None


class Item(AbstractBase):
    name: str
    quantity: int

    class Config:
        from_attributes = True


class Order(AbstractBase):
    id: int | None = None
    user: str
    item: str
    amount: int
    total: int
    status: str = "Incomplete"
    error: str | None = None
