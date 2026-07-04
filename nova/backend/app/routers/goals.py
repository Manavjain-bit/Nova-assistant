from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.habit_goal import Goal, Milestone
from app.models.user import User
from app.schemas.habit_goal import GoalCreate, GoalUpdate, GoalOut, MilestoneCreate, MilestoneOut

router = APIRouter(prefix="/goals", tags=["goals"])


def _recompute_progress(goal: Goal) -> None:
    if not goal.milestones:
        return
    completed = sum(1 for m in goal.milestones if m.is_completed)
    goal.progress_percentage = round((completed / len(goal.milestones)) * 100, 2)


@router.post("", response_model=GoalOut, status_code=201)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = Goal(user_id=user.id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("", response_model=list[GoalOut])
def list_goals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Goal).filter(Goal.user_id == user.id).all()


@router.get("/{goal_id}", response_model=GoalOut)
def get_goal(goal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.patch("/{goal_id}", response_model=GoalOut)
def update_goal(goal_id: int, payload: GoalUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return None


@router.post("/{goal_id}/milestones", response_model=MilestoneOut, status_code=201)
def add_milestone(goal_id: int, payload: MilestoneCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    milestone = Milestone(goal_id=goal.id, **payload.model_dump())
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.patch("/{goal_id}/milestones/{milestone_id}/complete", response_model=MilestoneOut)
def complete_milestone(goal_id: int, milestone_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id, Milestone.goal_id == goal_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    milestone.is_completed = True
    db.commit()
    db.refresh(goal)
    _recompute_progress(goal)
    db.commit()
    db.refresh(milestone)
    return milestone
