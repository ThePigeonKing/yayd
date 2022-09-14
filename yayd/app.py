from textwrap import indent
from fastapi import FastAPI, Depends, status, HTTPException
from .database import ItemBase, BatchElem, get_db_session, Item, ItemType
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import json

import uvicorn

app = FastAPI()

@app.post('/imports', status_code=status.HTTP_200_OK)
def import_items(data: BatchElem, session: Session = Depends(get_db_session)):
    error = False
    for item in data.items:
        statement = select(Item).where(Item.id == item.id)
        existing = session.exec(statement).first()
        # help(existing)
        try:
            if existing is None:
                item = Item(**item.dict())
                item.updateDate = data.updateDate
                statement = select(Item).where(Item.id == item.parentId)
                parent = session.exec(statement).first()
                if parent.type == ItemType.file:
                    session.rollback()
                    raise HTTPException(status_code=400, detail="Parent can't be FILE")
                session.add(item)
            else:
                for key, value in item.dict().items():
                    setattr(existing, key, value)
                session.add(existing)
        except IntegrityError as exc:
                session.rollback()
                error = True
                raise HTTPException(status_code=400, detail="parentId doesn't exist")

    if error == False:
        session.commit()   
                    
    return

@app.get("/nodes/{id:str}")
def get_info(id, session: Session = Depends(get_db_session)):
    try:
        id = UUID(id)
        statement = select(Item).where(Item.id == id)
        res = session.exec(statement).first()
        if res is None:
            return HTTPException(status_code=400, detail="id doen't exist")
        else:
            return res
    except ValueError as exc:
        return HTTPException(status_code=400, detail="Bad id given")

def main():
    uvicorn.run("yayd.app:app", host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()