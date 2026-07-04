from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.services.prioritization import rescore_task, rescore_all_for_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.parent_id is not None:
        parent = db.query(Task).filter(Task.id == payload.parent_id, Task.user_id == user.id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent task not found")

    task = Task(user_id=user.id, **payload.model_dump())
    rescore_task(task)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status: str | None = None,
    category: str | None = None,
    prioritized: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if prioritized:
        return rescore_all_for_user(db, user.id)

    query = db.query(Task).filter(Task.user_id == user.id)
    if status:
        query = query.filter(Task.status == status)
    if category:
        query = query.filter(Task.category == category)
    return query.order_by(Task.priority_score.desc()).all()


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}/subtasks", response_model=list[TaskOut])
def get_subtasks(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    parent = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Task not found")
    return db.query(Task).filter(Task.parent_id == task_id).all()


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    rescore_task(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None
