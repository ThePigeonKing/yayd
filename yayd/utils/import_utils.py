from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from ..database import Item


def get_parent(parentId: UUID | None, session: Session) -> Item:
    statement = select(Item).where(Item.id == parentId)
    parent = session.exec(statement).first()
    return parent


# add size for all parent & co.
def increase_size(parentId: UUID, size: int, session: Session):
    parent = get_parent(parentId, session)
    if parent is None:
        return
    else:
        current_size = 0 if parent.size is None else parent.size
        setattr(parent, "size", current_size + size)
        session.add(parent)
        increase_size(parent.parentId, size, session)


def decrease_size(parentId: UUID, old_size: int, session: Session):
    parent = get_parent(parentId, session)
    if parent is None:
        return
    else:
        current_size = 0 if parent.size is None else parent.size
        setattr(parent, "size", current_size - old_size)
        session.add(parent)
        decrease_size(parent.parentId, old_size, session)


def reset_data_update(item: Item, new_date: datetime, session: Session):
    if item is None:
        return
    setattr(item, "updateDate", new_date)
    session.add(item)
    parent = get_parent(item.parentId, session)
    if parent is None:
        return
    else:
        reset_data_update(parent, new_date, session)
