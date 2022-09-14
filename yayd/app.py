from fastapi import FastAPI, Depends, status
from .database import ItemBase, BatchElem, get_db_session, Item


from sqlmodel import Session, select
from uuid import UUID

import uvicorn

app = FastAPI()

@app.post('/imports', status_code=status.HTTP_200_OK)
def import_items(data: BatchElem, session: Session = Depends(get_db_session),):
    for item in data.items:
        statement = select(Item).where(Item.id == item.id)
        existing = session.exec(statement).first()
        # help(existing)
        if existing is None:
            item = Item(**item.dict())
            item.updateDate = data.updateDate
            session.add(item)
        else:
            for key, value in item.dict().items():
                setattr(existing, key, value)
            session.add(existing)

    session.commit()

    return


# @app.get("/delete/{id:UUID}")
# def 

def main():
    uvicorn.run("yayd.app:app", host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()