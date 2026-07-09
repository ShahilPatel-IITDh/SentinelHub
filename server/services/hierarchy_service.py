from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.models import User


def can_monitor_user(senior: User, junior: User) -> bool:
    if not senior or not junior:
        return False

    if not senior.post or not junior.post:
        return False

    if not senior.post.can_monitor:
        return False

    # Direct junior rule
    if junior.reporting_officer_id != senior.employee_id:
        return False

    # Senior must have higher level
    if senior.post.level <= junior.post.level:
        return False

    return True


def get_direct_monitorable_junior_ids(db: Session, senior: User):
    juniors = (
        db.query(User)
        .filter(User.reporting_officer_id == senior.employee_id)
        .all()
    )

    allowed_ids = []

    for junior in juniors:

        if can_monitor_user(senior, junior):
            allowed_ids.append(junior.employee_id)

    return allowed_ids


def validate_reporting_assignment(employee: User, officer: User):
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not officer:
        raise HTTPException(status_code=404, detail="Reporting officer not found")

    if employee.employee_id == officer.employee_id:
        raise HTTPException(
            status_code=400,
            detail="Employee cannot report to themselves"
        )

    if not employee.post or not officer.post:
        raise HTTPException(
            status_code=400,
            detail="Both employee and reporting officer must have posts assigned"
        )

    if officer.post.level <= employee.post.level:
        raise HTTPException(
            status_code=400,
            detail="Reporting officer must have a higher hierarchy level"
        )