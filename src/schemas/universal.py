from pydantic import BaseModel


class MessageSchema(BaseModel):
    """Pydantic схема для отображения простых сообщений."""

    detail: str
