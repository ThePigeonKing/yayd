from uuid import UUID

from sqlmodel import Session, select

from ..database import Item, ItemType, date_format


def get_all_children(current: Item, session: Session):
    statement = select(Item).where(Item.parentId == current.id)
    elems = session.exec(statement).all()
    result = []
    for i in elems:
        current = dict(i)
        current["date"] = current.pop("updateDate").strftime(date_format)
        if i.type == ItemType.file:
            current.update({"children": None})
        elif i.type == ItemType.folder:
            children = get_all_children(i, session)
            current.update({"children": children})
        result.append(current)
    return result
