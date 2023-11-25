from pydantic import BaseModel


class AbstractBase(BaseModel):
    id: int | None = None


class Delivery(AbstractBase):
    username: str
    status: str

    class Config:
        from_attributes = True
