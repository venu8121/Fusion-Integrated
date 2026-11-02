from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="CourseWorkspace", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("course_id", models.PositiveBigIntegerField(db_index=True, unique=True)),
            ("course_code", models.CharField(blank=True, max_length=40)),
            ("title", models.CharField(max_length=200)),
            ("description", models.TextField(blank=True)),
            ("syllabus", models.TextField(blank=True)),
            ("schedule", models.JSONField(blank=True, default=list)),
            ("updated_at", models.DateTimeField(auto_now=True)),
        ], options={"db_table": "lms_course_workspace"}),
        migrations.CreateModel(name="CourseStaff", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("course_id", models.PositiveBigIntegerField(db_index=True)),
            ("user_id", models.PositiveBigIntegerField(db_index=True)),
            ("role", models.CharField(choices=[("faculty", "Faculty"), ("ta", "Teaching Assistant"), ("observer", "Observer")], max_length=16)),
        ], options={"db_table": "lms_course_staff"}),
        migrations.AddConstraint(model_name="coursestaff", constraint=models.UniqueConstraint(fields=("course_id", "user_id", "role"), name="lms_unique_course_staff_role")),
        migrations.CreateModel(name="CourseMaterial", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("course_id", models.PositiveBigIntegerField(db_index=True)),
            ("title", models.CharField(max_length=200)),
            ("kind", models.CharField(choices=[("file", "File"), ("link", "Link"), ("note", "Note")], max_length=12)),
            ("section", models.CharField(blank=True, max_length=120)),
            ("content", models.TextField(blank=True)),
            ("url", models.URLField(blank=True)),
            ("file", models.FileField(blank=True, upload_to="lms/materials/")),
            ("release_at", models.DateTimeField(blank=True, null=True)),
            ("status", models.CharField(default="draft", max_length=12)),
            ("created_by", models.PositiveBigIntegerField()),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"db_table": "lms_course_material"}),
        migrations.CreateModel(name="Announcement", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("course_id", models.PositiveBigIntegerField(db_index=True)),
            ("title", models.CharField(max_length=200)),
            ("body", models.TextField()),
            ("posted_by", models.PositiveBigIntegerField()),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"db_table": "lms_announcement", "ordering": ["-created_at"]}),
        migrations.CreateModel(name="Assignment", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("course_id", models.PositiveBigIntegerField(db_index=True)),
            ("title", models.CharField(max_length=200)),
            ("instructions", models.TextField()),
            ("due_at", models.DateTimeField()),
            ("release_at", models.DateTimeField(blank=True, null=True)),
            ("submission_type", models.CharField(choices=[("file", "File"), ("text", "Text"), ("link", "Link")], max_length=8)),
            ("points_possible", models.DecimalField(decimal_places=2, max_digits=8)),
            ("attachment", models.FileField(blank=True, upload_to="lms/assignments/")),
            ("status", models.CharField(default="draft", max_length=12)),
            ("published_at", models.DateTimeField(blank=True, null=True)),
            ("created_by", models.PositiveBigIntegerField()),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"db_table": "lms_assignment"}),
        migrations.CreateModel(name="Submission", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("student_id", models.PositiveBigIntegerField(db_index=True)),
            ("text_response", models.TextField(blank=True)),
            ("link_url", models.URLField(blank=True)),
            ("file", models.FileField(blank=True, upload_to="lms/submissions/")),
            ("submitted_at", models.DateTimeField(default=django.utils.timezone.now)),
            ("assignment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="lms.assignment")),
        ], options={"db_table": "lms_submission"}),
        migrations.AddConstraint(model_name="submission", constraint=models.UniqueConstraint(fields=("assignment", "student_id"), name="lms_one_submission_per_student")),
        migrations.CreateModel(name="Grade", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("points", models.DecimalField(decimal_places=2, max_digits=8)),
            ("feedback", models.TextField(blank=True)),
            ("status", models.CharField(default="draft", max_length=10)),
            ("graded_by", models.PositiveBigIntegerField()),
            ("graded_at", models.DateTimeField(auto_now=True)),
            ("released_at", models.DateTimeField(blank=True, null=True)),
            ("submission", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="grade", to="lms.submission")),
        ], options={"db_table": "lms_grade"}),
        migrations.CreateModel(name="GradeAudit", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("actor_id", models.PositiveBigIntegerField()),
            ("changed_at", models.DateTimeField(auto_now_add=True)),
            ("old_points", models.DecimalField(decimal_places=2, max_digits=8)),
            ("new_points", models.DecimalField(decimal_places=2, max_digits=8)),
            ("old_feedback", models.TextField(blank=True)),
            ("new_feedback", models.TextField(blank=True)),
            ("grade", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="audit", to="lms.grade")),
        ], options={"db_table": "lms_grade_audit"}),
    ]
