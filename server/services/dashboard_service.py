from sqlalchemy.orm import Session

from db.models import User

from services.summary_service import get_summary_for_employee_ids
from services.log_service import get_logs_for_employee_ids
from services.metrics_service import get_metrics_for_employee_ids
from services.error_service import get_errors_for_employee_ids

from services.hierarchy_service import get_direct_monitorable_junior_ids


def get_dashboard_live_data(
    db: Session,
    user: User
):
    """
    Returns all dashboard data in a single response.
    """

    junior_ids = get_direct_monitorable_junior_ids(db, user)

    return {
        "summary": get_summary_for_employee_ids(
            db,
            junior_ids
        ),
        "logs": get_logs_for_employee_ids(
            db,
            junior_ids
        ),
        "metrics": get_metrics_for_employee_ids(
            db,
            junior_ids
        ),
        "errors": get_errors_for_employee_ids(
            db,
            junior_ids
        )
    }