# LMS Course Management

This module provides course workspaces, materials, announcements, assignments,
student submissions, grading, grade release, and scheduled content publication.

## Integration prerequisite

The LMS deliberately does not create a parallel course-enrollment system.
Configure `LMS_COURSE_ACCESS_PROVIDER` as a dotted Python import path to a
callable accepting `(user_id, course_id, principal_kind)` and returning
exactly `True` for authorized access. Until configured, course access fails
closed. The provider must apply the approved student, staff, and observer
linkage rules.

## API

Mounted at `/api/v1/lms/`. Course IDs refer to the canonical Fusion course
records. See `api/urls.py` for supported endpoints.

## Policy items intentionally not assumed

The v1.0 specification issue register leaves late-submission behavior,
resubmission rules, observer linkage granularity, and post-release grade
change authority unresolved. The API refuses late submissions, repeat
submissions, and post-release grade changes with explicit policy messages
rather than silently selecting a policy.

## Scheduled release

The Celery task `lms.process_scheduled_content` publishes scheduled course
materials and makes scheduled assignments available. It runs once per minute
through the merged Celery Beat schedule.
