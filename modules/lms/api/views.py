from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from fusion_auth.permissions import HasModuleGrant, HasPermission
from modules.lms.course_access import CourseAccessUnavailable, has_course_access, has_staff_role
from modules.lms.models import CourseWorkspace, CourseMaterial, Announcement, Assignment, Submission, Grade
from modules.lms.api.serializers import CourseWorkspaceSerializer, CourseMaterialSerializer, AnnouncementSerializer, AssignmentSerializer, SubmissionSerializer, GradeSerializer

MODULE=HasModuleGrant("lms_course_management")
VIEW="lms_course_management.course.view"
def principal(request): return request.principal
def course_access(request, course_id):
    try: allowed=has_course_access(principal(request),course_id)
    except CourseAccessUnavailable as exc: raise PermissionDenied(str(exc))
    if not allowed: raise NotFound("Course not found.")
def staff(request, course_id, *roles):
    if not any(has_staff_role(principal(request),course_id,r) for r in roles): raise NotFound("Course not found.")
def require(p, permission):
    if not p.has_permission(permission): raise PermissionDenied()

class CourseView(APIView):
    permission_classes=[MODULE,HasPermission(VIEW)]
    def get(self,request,course_id):
        course_access(request,course_id)
        obj=CourseWorkspace.objects.filter(course_id=course_id).first()
        if not obj: raise NotFound("Course workspace not configured.")
        return Response(CourseWorkspaceSerializer(obj).data)
    def put(self,request,course_id):
        course_access(request,course_id); staff(request,course_id,"faculty")
        require(principal(request),"lms_course_management.course.manage")
        obj=CourseWorkspace.objects.filter(course_id=course_id).first()
        if not obj: raise NotFound("Course workspace not configured.")
        s=CourseWorkspaceSerializer(obj,data=request.data,partial=True); s.is_valid(raise_exception=True); s.save()
        return Response(s.data)

class MaterialsView(APIView):
    permission_classes=[MODULE,HasPermission(VIEW)]
    def get(self,request,course_id):
        course_access(request,course_id); now=timezone.now()
        qs=CourseMaterial.objects.filter(course_id=course_id,status="published").filter(release_at__isnull=True)|CourseMaterial.objects.filter(course_id=course_id,status="published",release_at__lte=now)
        return Response(CourseMaterialSerializer(qs.distinct(),many=True).data)
    def post(self,request,course_id):
        course_access(request,course_id); staff(request,course_id,"faculty")
        require(principal(request),"lms_course_management.material.manage")
        s=CourseMaterialSerializer(data=request.data); s.is_valid(raise_exception=True)
        release=s.validated_data.get("release_at")
        obj=s.save(course_id=course_id,created_by=principal(request).user_id,status="scheduled" if release and release>timezone.now() else "published")
        return Response(CourseMaterialSerializer(obj).data,status=201)

class AnnouncementsView(APIView):
    permission_classes=[MODULE,HasPermission(VIEW)]
    def get(self,request,course_id):
        course_access(request,course_id)
        return Response(AnnouncementSerializer(Announcement.objects.filter(course_id=course_id),many=True).data)
    def post(self,request,course_id):
        course_access(request,course_id); staff(request,course_id,"faculty","ta")
        require(principal(request),"lms_course_management.announcement.post")
        s=AnnouncementSerializer(data=request.data); s.is_valid(raise_exception=True)
        obj=s.save(course_id=course_id,posted_by=principal(request).user_id)
        return Response(AnnouncementSerializer(obj).data,status=201)

class AssignmentsView(APIView):
    permission_classes=[MODULE,HasPermission(VIEW)]
    def get(self,request,course_id):
        course_access(request,course_id); now=timezone.now()
        qs=Assignment.objects.filter(course_id=course_id).exclude(status="draft").filter(release_at__isnull=True)|Assignment.objects.filter(course_id=course_id,status__in=["scheduled","available"],release_at__lte=now)
        return Response(AssignmentSerializer(qs.distinct(),many=True).data)
    def post(self,request,course_id):
        course_access(request,course_id); staff(request,course_id,"faculty")
        require(principal(request),"lms_course_management.assignment.manage")
        s=AssignmentSerializer(data=request.data); s.is_valid(raise_exception=True)
        if s.validated_data["points_possible"]<0: raise ValidationError({"points_possible":"Must be zero or greater."})
        obj=s.save(course_id=course_id,created_by=principal(request).user_id,status="draft")
        return Response(AssignmentSerializer(obj).data,status=201)

class AssignmentDetailView(APIView):
    permission_classes=[MODULE,HasPermission(VIEW)]
    def patch(self,request,course_id,assignment_id):
        course_access(request,course_id); staff(request,course_id,"faculty")
        require(principal(request),"lms_course_management.assignment.manage")
        obj=Assignment.objects.filter(pk=assignment_id,course_id=course_id,status="draft").first()
        if not obj: raise NotFound("Draft assignment not found.")
        s=AssignmentSerializer(obj,data=request.data,partial=True); s.is_valid(raise_exception=True); s.save()
        return Response(s.data)
    def post(self,request,course_id,assignment_id):
        course_access(request,course_id); staff(request,course_id,"faculty")
        require(principal(request),"lms_course_management.assignment.manage")
        obj=Assignment.objects.filter(pk=assignment_id,course_id=course_id,status="draft").first()
        if not obj: raise NotFound("Draft assignment not found.")
        obj.published_at=timezone.now(); obj.status="scheduled" if obj.release_at and obj.release_at>timezone.now() else "available"
        obj.save(update_fields=["published_at","status","updated_at"])
        return Response(AssignmentSerializer(obj).data)

class SubmitView(APIView):
    permission_classes=[MODULE,HasPermission("lms_course_management.submission.create")]
    def post(self,request,course_id,assignment_id):
        course_access(request,course_id); p=principal(request)
        if p.kind!="student": raise PermissionDenied()
        obj=Assignment.objects.filter(pk=assignment_id,course_id=course_id,status="available").first()
        if not obj: raise NotFound("Available assignment not found.")
        if obj.due_at<=timezone.now(): raise ValidationError("Late-submission policy is unresolved; submission was not accepted.")
        payload={"file":request.data.get("file"),"text_response":request.data.get("text_response",""),"link_url":request.data.get("link_url","")}
        required={"file":"file","text":"text_response","link":"link_url"}[obj.submission_type]
        if not payload[required]: raise ValidationError({required:"This submission field is required."})
        if Submission.objects.filter(assignment=obj,student_id=p.user_id).exists():
            raise ValidationError("Resubmission policy is unresolved; an existing submission was found.")
        row=Submission.objects.create(assignment=obj,student_id=p.user_id,**payload)
        return Response(SubmissionSerializer(row).data,status=201)

class SubmissionHistoryView(APIView):
    permission_classes=[MODULE,HasPermission("lms_course_management.submission.create")]
    def get(self,request,course_id,assignment_id):
        course_access(request,course_id)
        rows=Submission.objects.filter(assignment_id=assignment_id,assignment__course_id=course_id,student_id=principal(request).user_id)
        return Response(SubmissionSerializer(rows,many=True).data)

class CourseSubmissionsView(APIView):
    permission_classes=[MODULE,HasPermission("lms_course_management.submission.view_course")]
    def get(self,request,course_id,assignment_id):
        course_access(request,course_id); staff(request,course_id,"faculty","ta")
        rows=Submission.objects.filter(assignment_id=assignment_id,assignment__course_id=course_id)
        return Response(SubmissionSerializer(rows,many=True).data)

class GradeView(APIView):
    permission_classes=[MODULE,HasPermission("lms_course_management.grade.manage")]
    def put(self,request,course_id,submission_id):
        course_access(request,course_id); p=principal(request); staff(request,course_id,"faculty","ta")
        row=Submission.objects.filter(pk=submission_id,assignment__course_id=course_id).first()
        if not row: raise NotFound("Submission not found.")
        if hasattr(row,"grade") and row.grade.status=="released":
            raise ValidationError("Post-release grade-change authority is unresolved; grade is locked.")
        try: points=float(request.data["points"])
        except (KeyError,TypeError,ValueError): raise ValidationError({"points":"A valid score is required."})
        if points<0 or points>float(row.assignment.points_possible): raise ValidationError({"points":"Score outside allowed range."})
        grade,_=Grade.objects.update_or_create(submission=row,defaults={"points":points,"feedback":request.data.get("feedback",""),"graded_by":p.user_id,"status":"draft"})
        return Response(GradeSerializer(grade).data)

class ReleaseGradesView(APIView):
    permission_classes=[MODULE,HasPermission("lms_course_management.grade.release")]
    def post(self,request,course_id,assignment_id):
        course_access(request,course_id); staff(request,course_id,"faculty")
        count=Grade.objects.filter(submission__assignment_id=assignment_id,submission__assignment__course_id=course_id,status="draft").update(status="released",released_at=timezone.now())
        return Response({"released_count":count})

class MyGradesView(APIView):
    permission_classes=[MODULE,HasPermission("lms_course_management.grade.view_self")]
    def get(self,request,course_id):
        course_access(request,course_id)
        rows=Grade.objects.filter(submission__student_id=principal(request).user_id,submission__assignment__course_id=course_id,status="released")
        return Response(GradeSerializer(rows,many=True).data)
