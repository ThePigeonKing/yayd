from uuid import UUID

from sqlmodel import Session, select

from ..database import Item, ItemType


def delete_all_related(current: Item, session: Session):
    statement = select(Item).where(Item.parentId == current.id)
    all_related = session.exec(statement).all()
    for elem in all_related:
        if elem.type == ItemType.file:
            session.delete(elem)
        elif elem.type == ItemType.folder:
            delete_all_related(elem, session)
            session.delete(elem)
