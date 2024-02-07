from uuid import UUID

from pydantic import BaseModel


class DefaultModelSchema(BaseModel):
    id: UUID
    title: str
    description: str


class MessageSchema(BaseModel):
    """Pydantic схема для отображения простых сообщений."""

    detail: str
