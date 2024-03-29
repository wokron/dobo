from pathlib import Path
from sqlmodel import Field, Relationship, SQLModel

from app.core.config import settings


class DocumentSet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=64, unique=True)

    chats: list["Chat"] = Relationship(back_populates="document_set")
    documents: list["Document"] = Relationship(back_populates="document_set")

    def get_save_path(self) -> Path:
        return Path(settings.DATA_DIR) / "docsets" / self.id


class DocumentSetCreate(SQLModel):
    name: str = Field(max_length=64)


class DocumentSetOut(SQLModel):
    id: int
    name: str


class Document(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=64, unique=True)

    document_set_id: int = Field(primary_key=True, foreign_key="document_set.id")
    document_set: DocumentSet = Relationship(back_populates="documents")
    pages: list["Page"] = Relationship(back_populates="document")

    def get_save_path(self) -> Path:
        return self.document_set.get_save_path() / "docs" / self.name


class DocumentOut(SQLModel):
    id: int
    name: str
    document_set_id: int


class Page(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    document_id: int = Field(primary_key=True, foreign_key="document.id")
    document: Document = Relationship(back_populates="pages")


class Chat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=64, unique=True)

    document_set_id: int = Field(foreign_key="document_set.id")
    document_set: DocumentSet = Relationship(back_populates="chats")


class ChatCreate(SQLModel):
    name: str = Field(max_length=64)
    document_set_id: int


class ChatOut(SQLModel):
    id: int
    name: str
    document_set_id: int


class MessageIn(SQLModel):
    content: str


class MessageOut(SQLModel):
    role: str
    content: str
