import json
from datetime import datetime, timedelta
from textwrap import indent
from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, delete, select

from .database import (BatchElem, Item, ItemBase, ItemType, date_format,
                       get_db_session)
from .utils.delete_utils import delete_all_related
from .utils.import_utils import (decrease_size, get_parent, increase_size,
                                 reset_data_update)
from .utils.nodes_utils import get_all_children

app = FastAPI()


@app.post("/imports", status_code=200)
def import_items(data: BatchElem, session: Session = Depends(get_db_session)):
    for item in data.items:
        statement = select(Item).where(Item.id == item.id)
        existing = session.exec(statement).first()
        if existing is None:
            # creating new item
            item = Item(**item.dict())
            item.updateDate = data.updateDate
            if item.parentId is not None:
                parent = get_parent(item.parentId, session)
                if parent is None:
                    session.rollback()
                    raise HTTPException(status_code=400, detail="Parent doesn't exist")
                elif parent.type == ItemType.file:
                    session.rollback()
                    raise HTTPException(status_code=400, detail="Parent can't be FILE")
            session.add(item)
            if item.type == ItemType.file and item.parentId is not None:
                increase_size(item.parentId, item.size, session)
            reset_data_update(item, data.updateDate, session)
        else:
            # updating item
            if item.type != existing.type:
                session.rollback()
                raise HTTPException(
                    status_code=400, detail="Item type can't be changed"
                )
            if item.type == ItemType.file:
                # update size for all !OLD! parents
                decrease_size(existing.parentId, existing.size, session)
            for key, value in item.dict().items():
                setattr(existing, key, value)
            if item.type == ItemType.file:
                increase_size(item.parentId, item.size, session)
                session.add(existing)
            reset_data_update(existing, data.updateDate, session)

    session.commit()
    return


@app.delete("/delete/{id:str}")
def delete_item(id: str, date: datetime, session: Session = Depends(get_db_session)):
    statement = select(Item).where(Item.id == id)
    delete_head = session.exec(statement).first()
    if delete_head is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        decrease_size(delete_head.parentId, delete_head.size, session)
        if delete_head.type == ItemType.file:
            session.delete(delete_head)
        elif delete_head.type == ItemType.folder:
            delete_all_related(delete_head, session)
            session.delete(delete_head)
    session.commit()


@app.get("/nodes/{id:str}")
def get_info(id: str, session: Session = Depends(get_db_session)):
    return_tree = {}
    statement = select(Item).where(Item.id == id)
    headelem = session.exec(statement).first()
    if headelem is None:
        raise HTTPException(status_code=400, detail="id doen't exist")
    else:
        dicted = dict(headelem)
        dicted["date"] = dicted.pop("updateDate").strftime(date_format)
        return_tree.update(dicted)
        if headelem.type == ItemType.folder:
            children = get_all_children(headelem, session)
            return_tree.update({"children": children})
        else:
            return_tree.update({"children": None})
        return return_tree


@app.get("/updates")
def get_updates(date: datetime, session: Session = Depends(get_db_session)):
    delta = timedelta(1)
    leftlim = date - delta
    statement = select(Item).where(Item.updateDate <= date, Item.updateDate >= leftlim)
    items = session.exec(statement)
    return items.all()


def main():
    uvicorn.run("yayd.app:app", host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
