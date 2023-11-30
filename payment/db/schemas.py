from pydantic import BaseModel


class AbstractBase(BaseModel):
    id: int | None = None


class Payment(AbstractBase):
    user_id: int
    item: str
    status: str = "Completed"

    class Config:
        from_attributes = True


class User(AbstractBase):
    username: str
    credit: int = 100

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
