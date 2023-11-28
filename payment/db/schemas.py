from pydantic import BaseModel


class AbstractBase(BaseModel):
    id: int | None = None


class Payment(AbstractBase):
    user_id: int
    item: str
    status: str

    class Config:
        from_attributes = True


class User(AbstractBase):
    username: str
    credit: int
    payments: list[Payment] = []

    class Config:
        from_attributes = True


class Order(AbstractBase):
    id: int | None = None
    user: str
    item: str
    amount: int
    total: int
    status: str = "Incomplete"
