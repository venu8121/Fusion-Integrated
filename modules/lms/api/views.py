from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from fusion_auth.permissions import HasModuleGrant, HasPermission
from modules.lms.course_access import CourseAccessUnavailable, has_course_access, has_staff_role
from modules.lms.models import (
    Announcement, Assignment, CourseMaterial, CourseStaff, CourseWorkspace,
    Grade, GradeAudit, Submission,
)
from modules.lms.api.serializers import (
    AnnouncementSerializer, AssignmentSerializer, CourseMaterialSerializer,
    CourseWorkspaceSerializer, GradeSerializer, SubmissionSerializer,
)

MODULE = HasModuleGrant("lms_course_management")
VIEW = "lms_course_management.course.view"
MATERIAL = "lms_course_management.material.manage"
ANNOUNCE = "lms_course_management.announcement.post"
ASSIGNMENT = "lms_course_management.assignment.manage"
SUBMIT = "lms_course_management.submission.create"
VIEW_SUBMISSIONS = "lms_course_management.submission.view_course"
GRADE = "lms_course_management.grade.manage"
RELEASE = "lms_course_management.grade.release"
VIEW_GRADE = "lms_course_management.grade.view_self"


def actor(request):
    return request.principal


def course_or_404(request, course_id):
    try:
        allowed = has_course_access(actor(request), course_id)
    except CourseAccessUnavailable as exc:
        raise PermissionDenied(str(exc)) from exc
    if not allowed:
        raise NotFound("Course not found.")


def require_staff(request, course_id, roles=("faculty",)):
    if not any(has_staff_role(actor(request), course_id, role) for role in roles):
        raise NotFound("Course not found.")


class CourseView(APIView):
    permission_classes = [MODULE, HasPermission(VIEW)]

    def get(self, request, course_id):
        course_or_404(request, course_id)
        item = CourseWorkspace.objects.filter(course_id=course_id).first()
        if not item:
            raise NotFound("Course workspace not found.")
        return Response(CourseWorkspaceSerializer(item).data)

    def put(self, request, course_id):
        course_or_404(request, course_id)
        require_staff(request, course_id)
        item = CourseWorkspace.objects.filter(course_id=course_id).first()
        serializer = CourseWorkspaceSerializer(item, data=request.data, partial=bool(item))
        serializer.is_valid(raise_exception=True)
        return Response(CourseWorkspaceSerializer(
            serializer.save(course_id=course_id)).data)


class MaterialsView(APIView):
    permission_classes = [MODULE, HasPermission(VIEW)]

    def get(self, request, course_id):
        course_or_404(request, course_id)
        now = timezone.now()
        rows = CourseMaterial.objects.filter(course_id=course_id, status="published")
        rows = rows.filter(release_at__isnull=True) | rows.filter(release_at__lte=now)
        return Response(CourseMaterialSerializer(rows.distinct(), many=True).data)

    def post(self, request, course_id):
        course_or_404(request, course_id)
        require_staff(request, course_id)
        if not actor(request).has_permission(MATERIAL):
            raise PermissionDenied()
        serializer = CourseMaterialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        release = serializer.validated_data.get("release_at")
        state = "scheduled" if release and release > timezone.now() else "published"
        item = serializer.save(course_id=course_id, created_by=actor(request).user_id,
                               status=state)
        return Response(CourseMaterialSerializer(item).data, status=201)


class AnnouncementsView(APIView):
    permission_classes = [MODULE, HasPermission(VIEW)]

    def get(self, request, course_id):
        course_or_404(request, course_id)
        rows = Announcement.objects.filter(course_id=course_id)
        return Response(AnnouncementSerializer(rows, many=True).data)

    def post(self, request, course_id):
        course_or_404(request, course_id)
        require_staff(request, course_id, ("faculty", "ta"))
        if not actor(request).has_permission(ANNOUNCE):
            raise PermissionDenied()
        serializer = AnnouncementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(course_id=course_id, posted_by=actor(request).user_id)
        return Response(AnnouncementSerializer(item).data, status=201)


class AssignmentsView(APIView):
    permission_classes = [MODULE, HasPermission(VIEW)]

    def get(self, request, course_id):
        course_or_404(request, course_id)
        now = timezone.now()
        rows = Assignment.objects.filter(course_id=course_id).exclude(status="draft")
        rows = rows.filter(release_at__isnull=True) | rows.filter(release_at__lte=now)
        return Response(AssignmentSerializer(rows.distinct(), many=True).data)

    def post(self, request, course_id):
        course_or_404(request, course_id)
        require_staff(request, course_id)
        if not actor(request).has_permission(ASSIGNMENT):
            raise PermissionDenied()
        serializer = AssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["points_possible"] < 0:
            raise ValidationError({"points_possible": "Must be zero or greater."})
        item = serializer.save(course_id=course_id, created_by=actor(request).user_id,
                               status="draft")
        return Response(AssignmentSerializer(item).data, status=201)


class AssignmentDetailView(APIView):
    permission_classes = [MODULE, HasPermission(VIEW)]

    def patch(self, request, course_id, assignment_id):
        course_or_404(request, course_id)
        require_staff(request, course_id)
        if not actor(request).has_permission(ASSIGNMENT):
            raise PermissionDenied()
        item = Assignment.objects.filter(pk=assignment_id, course_id=course_id,
                                          status="draft").first()
        if not item:
            raise NotFound("Draft assignment not found.")
        serializer = AssignmentSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def post(self, request, course_id, assignment_id):
        course_or_404(request, course_id)
        require_staff(request, course_id)
        if not actor(request).has_permission(ASSIGNMENT):
            raise PermissionDenied()
        item = Assignment.objects.filter(pk=assignment_id, course_id=course_id,
                                          status="draft").first()
        if not item:
            raise NotFound("Draft assignment not found.")
        item.published_at = timezone.now()
        item.status = ("scheduled" if item.release_at and
                       item.release_at > timezone.now() else "available")
        item.save(update_fields=["published_at", "status"])
        return Response(AssignmentSerializer(item).data)


class SubmitView(APIView):
    permission_classes = [MODULE, HasPermission(SUBMIT)]

    def post(self, request, course_id, assignment_id):
        course_or_404(request, course_id)
        assignment = Assignment.objects.filter(course_id=course_id, pk=assignment_id,
            status="available", due_at__gt=timezone.now()).first()
        if not assignment:
            raise NotFound("Available assignment not found.")
        field = {"file": "file", "text": "text_response",
                 "link": "link_url"}[assignment.submission_type]
        if not request.data.get(field):
            raise ValidationError({field: "This submission field is required."})
        if Submission.objects.filter(assignment=assignment,
                student_id=actor(request).user_id).exists():
            raise ValidationError("A submission already exists. Resubmission policy is pending.")
        submission = Submission.objects.create(
            assignment=assignment, student_id=actor(request).user_id,
            file=request.data.get("file") if field == "file" else None,
            text_response=request.data.get("text_response", "") if field == "text_response" else "",
            link_url=request.data.get("link_url", "") if field == "link_url" else "",
        )
        return Response(SubmissionSerializer(submission).data, status=201)


class SubmissionHistoryView(APIView):
    permission_classes = [MODULE, HasPermission(SUBMIT)]

    def get(self, request, course_id, assignment_id):
        course_or_404(request, course_id)
        rows = Submission.objects.filter(assignment_id=assignment_id,
            assignment__course_id=course_id, student_id=actor(request).user_id)
        return Response(SubmissionSerializer(rows, many=True).data)


class CourseSubmissionsView(APIView):
    permission_classes = [MODULE, HasPermission(VIEW_SUBMISSIONS)]

    def get(self, request, course_id, assignment_id):
        course_or_404(request, course_id)
        require_staff(request, course_id, ("faculty", "ta"))
        rows = Submission.objects.filter(assignment_id=assignment_id,
            assignment__course_id=course_id)
        return Response(SubmissionSerializer(rows, many=True).data)


class GradeView(APIView):
    permission_classes = [MODULE, HasPermission(GRADE)]

    def put(self, request, course_id, submission_id):
        course_or_404(request, course_id)
        require_staff(request, course_id, ("faculty", "ta"))
        submission = Submission.objects.filter(pk=submission_id,
            assignment__course_id=course_id).first()
        if not submission:
            raise NotFound("Submission not found.")
        try:
            points = float(request.data.get("points"))
        except (TypeError, ValueError) as exc:
            raise ValidationError({"points": "A valid points value is required."}) from exc
        if points < 0 or points > float(submission.assignment.points_possible):
            raise ValidationError({"points": "Points are outside the allowed range."})
        feedback = request.data.get("feedback", "")
        with transaction.atomic():
            grade = Grade.objects.select_for_update().filter(submission=submission).first()
            if grade is None:
                grade = Grade.objects.create(submission=submission, points=points,
                    feedback=feedback, graded_by=actor(request).user_id)
            else:
                if grade.status == "released":
                    GradeAudit.objects.create(grade=grade, actor_id=actor(request).user_id,
                        old_points=grade.points, new_points=points,
                        old_feedback=grade.feedback, new_feedback=feedback)
                grade.points, grade.feedback = points, feedback
                grade.graded_by = actor(request).user_id
                grade.save()
        return Response(GradeSerializer(grade).data)


class ReleaseGradesView(APIView):
    permission_classes = [MODULE, HasPermission(RELEASE)]

    def post(self, request, course_id, assignment_id):
        course_or_404(request, course_id)
        require_staff(request, course_id)
        count = Grade.objects.filter(submission__assignment_id=assignment_id,
            submission__assignment__course_id=course_id, status="draft").update(
                status="released", released_at=timezone.now())
        return Response({"released_count": count})


class MyGradesView(APIView):
    permission_classes = [MODULE, HasPermission(VIEW_GRADE)]

    def get(self, request, course_id):
        course_or_404(request, course_id)
        rows = Grade.objects.filter(submission__student_id=actor(request).user_id,
            submission__assignment__course_id=course_id, status="released")
        return Response(GradeSerializer(rows, many=True).data)
