from pydantic import BaseModel


class AbstractBase(BaseModel):
    id: int | None = None


class Item(AbstractBase):
    name: str
    quantity: int

    class Config:
        from_attributes = True
