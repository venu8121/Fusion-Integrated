
"""Application operations for Employee Leave Management."""

from django.db import transaction
from django.utils import timezone

from modules.elm.models import LeaveApplication


class LeaveApplicationError(Exception):
    """Raised when a leave application cannot be processed."""


@transaction.atomic
def submit_leave(
    *,
    employee_id: str,
    leave_type: str,
    start_date,
    end_date,
    reason: str,
) -> LeaveApplication:
    """Create and submit a leave application."""
    if not employee_id.strip():
        raise LeaveApplicationError("Employee ID is required.")

    if not leave_type.strip():
        raise LeaveApplicationError("Leave type is required.")

    if end_date < start_date:
        raise LeaveApplicationError("End date cannot precede start date.")

    if not reason.strip():
        raise LeaveApplicationError("A reason for leave is required.")

    return LeaveApplication.objects.create(
        employee_id=employee_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason.strip(),
        status=LeaveApplication.Status.SUBMITTED,
        submitted_at=timezone.now(),
    )



@transaction.atomic
def decide_leave(
    *,
    application_id,
    approver_id: str,
    approve: bool,
    decision_note: str = "",
) -> LeaveApplication:
    """Record an approval or rejection decision."""
    application = LeaveApplication.objects.select_for_update().get(
        pk=application_id
    )

    if application.status != LeaveApplication.Status.SUBMITTED:
        raise LeaveApplicationError(
            "Only submitted applications can receive a decision."
        )

    if not approver_id.strip():
        raise LeaveApplicationError("Approver ID is required.")

    application.approver_id = approver_id
    application.decision_note = decision_note.strip()
    application.status = (
        LeaveApplication.Status.APPROVED
        if approve
        else LeaveApplication.Status.REJECTED
    )
    application.decided_at = timezone.now()
    application.save(
        update_fields=[
            "approver_id",
            "decision_note",
            "status",
            "decided_at",
            "updated_at",
        ]
    )

    return application
