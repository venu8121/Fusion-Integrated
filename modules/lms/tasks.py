from celery import shared_task
from django.utils import timezone
from modules.lms.models import Assignment, CourseMaterial


@shared_task(name="lms.process_scheduled_content")
def process_scheduled_content():
    now = timezone.now()
    materials = CourseMaterial.objects.filter(status="scheduled", release_at__lte=now)
    assignments = Assignment.objects.filter(status="scheduled", release_at__lte=now)
    return {"materials_released": materials.update(status="published"),
            "assignments_released": assignments.update(status="available")}
