"""LMS records reference Fusion users/courses by ID; no duplicate identity tables."""
from django.db import models
from django.utils import timezone


class CourseWorkspace(models.Model):
    course_id = models.PositiveBigIntegerField(unique=True, db_index=True)
    course_code = models.CharField(max_length=40, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    syllabus = models.TextField(blank=True)
    schedule = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lms_course_workspace"


class CourseStaff(models.Model):
    course_id = models.PositiveBigIntegerField(db_index=True)
    user_id = models.PositiveBigIntegerField(db_index=True)
    role = models.CharField(max_length=16, choices=[
        ("faculty", "Faculty"), ("ta", "Teaching Assistant"),
        ("observer", "Observer")])

    class Meta:
        db_table = "lms_course_staff"
        constraints = [models.UniqueConstraint(
            fields=["course_id", "user_id", "role"], name="lms_unique_course_staff_role")]


class CourseMaterial(models.Model):
    course_id = models.PositiveBigIntegerField(db_index=True)
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=12, choices=[
        ("file", "File"), ("link", "Link"), ("note", "Note")])
    section = models.CharField(max_length=120, blank=True)
    content = models.TextField(blank=True)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to="lms/materials/", blank=True)
    release_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, default="draft")
    created_by = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lms_course_material"


class Announcement(models.Model):
    course_id = models.PositiveBigIntegerField(db_index=True)
    title = models.CharField(max_length=200)
    body = models.TextField()
    posted_by = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lms_announcement"
        ordering = ["-created_at"]


class Assignment(models.Model):
    course_id = models.PositiveBigIntegerField(db_index=True)
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    due_at = models.DateTimeField()
    release_at = models.DateTimeField(null=True, blank=True)
    submission_type = models.CharField(max_length=8, choices=[
        ("file", "File"), ("text", "Text"), ("link", "Link")])
    points_possible = models.DecimalField(max_digits=8, decimal_places=2)
    attachment = models.FileField(upload_to="lms/assignments/", blank=True)
    status = models.CharField(max_length=12, default="draft")
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lms_assignment"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE,
                                   related_name="submissions")
    student_id = models.PositiveBigIntegerField(db_index=True)
    text_response = models.TextField(blank=True)
    link_url = models.URLField(blank=True)
    file = models.FileField(upload_to="lms/submissions/", blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "lms_submission"
        constraints = [models.UniqueConstraint(
            fields=["assignment", "student_id"], name="lms_one_submission_per_student")]


class Grade(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE,
                                      related_name="grade")
    points = models.DecimalField(max_digits=8, decimal_places=2)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=10, default="draft")
    graded_by = models.PositiveBigIntegerField()
    graded_at = models.DateTimeField(auto_now=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "lms_grade"


class GradeAudit(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="audit")
    actor_id = models.PositiveBigIntegerField()
    changed_at = models.DateTimeField(auto_now_add=True)
    old_points = models.DecimalField(max_digits=8, decimal_places=2)
    new_points = models.DecimalField(max_digits=8, decimal_places=2)
    old_feedback = models.TextField(blank=True)
    new_feedback = models.TextField(blank=True)

    class Meta:
        db_table = "lms_grade_audit"
