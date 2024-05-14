from pathlib import Path
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.config import settings


class DocumentSet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=64, unique=True)

    chats: list["Chat"] = Relationship(back_populates="document_set")
    documents: list["Document"] = Relationship(back_populates="document_set")

    def get_save_dir(self):
        return settings.data_dir / "docsets" / str(self.id)

    def get_documents_dir(self):
        return self.get_save_dir() / "docs"

    def get_vectorstore_dir(self):
        return self.get_save_dir() / "chroma"


class DocumentSetCreate(SQLModel):
    name: str = Field(max_length=64)


class DocumentSetOut(SQLModel):
    id: int
    name: str


class Document(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("document_set_id", "name"),)

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=64)
    page_num: int | None = Field(default=None, ge=0)

    document_set_id: int = Field(foreign_key="documentset.id")
    document_set: DocumentSet = Relationship(back_populates="documents")

    def get_save_path(self):
        documents_path: Path = self.document_set.get_documents_dir()
        return documents_path / self.name


class DocumentOut(SQLModel):
    id: int
    name: str
    document_set_id: int


class Chat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=64, unique=True)

    document_set_id: int = Field(foreign_key="documentset.id")
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


class DocumentOutWithPage(DocumentOut):
    pages: list[int]


class MessageOut(SQLModel):
    role: str
    content: str
    documents: list[DocumentOutWithPage]


class PagedDocumentOut(SQLModel):
    content: str
    page: int


class Keyword(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    keyword: str = Field(min_length=2, max_length=64, unique=True)
    prompt: str


class KeywordCreate(SQLModel):
    keyword: str = Field(min_length=2, max_length=64)
    prompt: str


class KeywordOut(SQLModel):
    id: int
    keyword: str
    prompt: str
