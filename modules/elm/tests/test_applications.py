"""Tests for Employee Leave Management application services."""

from datetime import date

import pytest

from modules.elm.models import LeaveApplication
from modules.elm.services.applications import (
    LeaveApplicationError,
    decide_leave,
    submit_leave,
)


@pytest.mark.django_db
def test_submit_leave_creates_submitted_application():
    application = submit_leave(
        employee_id="employee-001",
        leave_type="CL",
        start_date=date(2026, 11, 2),
        end_date=date(2026, 11, 3),
        reason="Personal work",
    )

    assert application.employee_id == "employee-001"
    assert application.leave_type == "CL"
    assert application.status == LeaveApplication.Status.SUBMITTED
    assert application.submitted_at is not None


@pytest.mark.django_db
def test_submit_leave_rejects_invalid_date_range():
    with pytest.raises(LeaveApplicationError):
        submit_leave(
            employee_id="employee-001",
            leave_type="CL",
            start_date=date(2026, 11, 4),
            end_date=date(2026, 11, 2),
            reason="Personal work",
        )


@pytest.mark.django_db
def test_decide_leave_approves_submitted_application():
    application = submit_leave(
        employee_id="employee-001",
        leave_type="CL",
        start_date=date(2026, 11, 2),
        end_date=date(2026, 11, 2),
        reason="Personal work",
    )

    decided = decide_leave(
        application_id=application.id,
        approver_id="approver-001",
        approve=True,
        decision_note="Approved",
    )

    assert decided.status == LeaveApplication.Status.APPROVED
    assert decided.approver_id == "approver-001"
    assert decided.decision_note == "Approved"
    assert decided.decided_at is not None
