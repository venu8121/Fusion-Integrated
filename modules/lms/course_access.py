"""Adapter boundary for Fusion's authoritative course enrolment service."""
from django.conf import settings
from django.utils.module_loading import import_string


class CourseAccessUnavailable(Exception):
    pass


def has_course_access(principal, course_id):
    path = getattr(settings, "LMS_COURSE_ACCESS_PROVIDER", "")
    if not path:
        raise CourseAccessUnavailable(
            "LMS_COURSE_ACCESS_PROVIDER must point to the Fusion course-registration adapter.")
    provider = import_string(path)
    return provider(principal.user_id, int(course_id), principal.kind) is True


def has_staff_role(principal, course_id, role):
    from modules.lms.models import CourseStaff
    return CourseStaff.objects.filter(
        course_id=course_id, user_id=principal.user_id, role=role).exists()
