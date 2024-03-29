from sqlmodel import Field, Relationship, SQLModel


class DocumentSet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=64, unique=True)

    chats: list["Chat"] = Relationship(back_populates="document_set")
    documents: list["Document"] = Relationship(back_populates="document_set")


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
