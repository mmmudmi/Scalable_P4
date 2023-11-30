from pydantic import BaseModel


class AbstractBase(BaseModel):
    id: int | None = None


class Order(AbstractBase):
    id: int | None = None
    user: str
    item: str
    amount: int
    total: int
    status: str = "Incomplete"
    error: str | None = None

    class Config:
        from_attributes = True
