from django.conf import settings
from django.utils.module_loading import import_string

class CourseAccessUnavailable(Exception):
    pass

def has_course_access(principal, course_id):
    # Deliberately delegates to Fusion's canonical registration/observer service.
    path = getattr(settings, "LMS_COURSE_ACCESS_PROVIDER", "")
    if not path:
        raise CourseAccessUnavailable("LMS_COURSE_ACCESS_PROVIDER is not configured.")
    provider = import_string(path)
    return provider(principal.user_id, int(course_id), principal.kind) is True

def has_staff_role(principal, course_id, role):
    from modules.lms.models import CourseStaff
    return CourseStaff.objects.filter(course_id=course_id,user_id=principal.user_id,role=role).exists()
