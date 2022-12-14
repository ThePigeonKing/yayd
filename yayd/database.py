from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import ValidationError, root_validator, validator
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel, create_engine

date_format = "%Y-%m-%dT%H:%M:%SZ"


class ItemType(Enum):
    file = "FILE"
    folder = "FOLDER"


class ItemBase(SQLModel):
    id: Optional[UUID] = Field(primary_key=True)
    type: ItemType = Field(...)
    parentId: UUID | None = Field(default=None)
    size: int | None = Field(default=None, ge=1)
    url: str | None = Field(default=None)

    @root_validator
    def validate_all(cls, values):
        if "type" not in values:
            raise ValueError("Required field type is invalid or not set")
        if values["type"] == ItemType.file:
            if "size" not in values or values["size"] is None:
                raise ValueError("Required field size is None")
            if "url" not in values or values["url"] is None:
                raise ValueError("Required field url is None")
            elif len(values["url"]) > 255:
                raise ValueError("url cant be longer 255 chars")
        elif values["type"] == ItemType.folder:
            if "size" in values and values["size"] is not None:
                raise ValueError("Field size must be None for folder")
            if "url" in values and values["url"] is not None:
                raise ValueError("Field url must be None for folder")

        return values


class Item(ItemBase, table=True):
    updateDate: datetime | None = Field(default=None)


class ItemRead(ItemBase):
    children: list[ItemBase] | None = Field(default=None)
    updateDate: datetime | None = Field(default=None)


class BatchElem(SQLModel):
    items: list[ItemBase]
    updateDate: datetime


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


Item.update_forward_refs

sqlite_file_name = "/data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)


def get_db_session():
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    key = ItemBase(
        id="069cb8d8-bbdd-47d3-ad8f-82ef4c269df2",
        type="FILE",
        parentId="069cb8d8-bbdd-47d3-ad8f-82ef4c269df3",
    )
