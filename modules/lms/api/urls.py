from django.urls import path
from modules.lms.api import views

urlpatterns = [
    path("courses/<int:course_id>", views.CourseView.as_view()),
    path("courses/<int:course_id>/materials", views.MaterialsView.as_view()),
    path("courses/<int:course_id>/announcements", views.AnnouncementsView.as_view()),
    path("courses/<int:course_id>/assignments", views.AssignmentsView.as_view()),
    path("courses/<int:course_id>/assignments/<int:assignment_id>",
         views.AssignmentDetailView.as_view()),
    path("courses/<int:course_id>/assignments/<int:assignment_id>/submit",
         views.SubmitView.as_view()),
    path("courses/<int:course_id>/assignments/<int:assignment_id>/history",
         views.SubmissionHistoryView.as_view()),
    path("courses/<int:course_id>/assignments/<int:assignment_id>/submissions",
         views.CourseSubmissionsView.as_view()),
    path("courses/<int:course_id>/submissions/<int:submission_id>/grade",
         views.GradeView.as_view()),
    path("courses/<int:course_id>/assignments/<int:assignment_id>/release-grades",
         views.ReleaseGradesView.as_view()),
    path("courses/<int:course_id>/grades", views.MyGradesView.as_view()),
]
