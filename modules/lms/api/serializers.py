from rest_framework import serializers
from modules.lms.models import CourseWorkspace, CourseMaterial, Announcement, Assignment, Submission, Grade

class CourseWorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model=CourseWorkspace
        fields=("course_id","course_code","title","description","syllabus","schedule","updated_at")
        read_only_fields=("course_id","updated_at")

class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model=CourseMaterial
        fields=("id","course_id","title","kind","section","content","url","file","release_at","status","created_by","created_at")
        read_only_fields=("id","course_id","status","created_by","created_at")

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model=Announcement
        fields=("id","course_id","title","body","posted_by","created_at")
        read_only_fields=("id","course_id","posted_by","created_at")

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Assignment
        fields=("id","course_id","title","instructions","due_at","release_at","submission_type","points_possible","attachment","status","published_at","created_by","created_at")
        read_only_fields=("id","course_id","status","published_at","created_by","created_at")

class SubmissionSerializer(serializers.ModelSerializer):
    assignment_id=serializers.IntegerField(read_only=True)
    class Meta:
        model=Submission
        fields=("id","assignment_id","student_id","text_response","link_url","file","status","submitted_at")
        read_only_fields=("id","assignment_id","student_id","status","submitted_at")

class GradeSerializer(serializers.ModelSerializer):
    submission_id=serializers.IntegerField(read_only=True)
    class Meta:
        model=Grade
        fields=("id","submission_id","points","feedback","status","graded_by","graded_at","released_at")
        read_only_fields=("id","submission_id","status","graded_by","graded_at","released_at")
