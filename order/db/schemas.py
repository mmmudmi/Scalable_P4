from pydantic import BaseModel


class AbstractBase(BaseModel):
    id: int | None = None


class Order(AbstractBase):
    id: int | None = None
    user: str
    item: str
    price: str
    status: str

    class Config:
        from_attributes = True
