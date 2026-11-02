MODULE = {"code":"lms_course_management","label":"LMS Course Management","icon":"FaBookOpen","base_path":"/lms","nav_section":"Academics","sort_order":30,"status":"active"}
NAV_ITEMS = [{"code":"lms.courses","label":"My Courses","icon":"FaBook","to":"/lms/courses","required_permission":"lms_course_management.course.view","sort_order":10}]
PERMISSIONS = [
("lms_course_management.course.view","View an authorized course workspace"),
("lms_course_management.course.manage","Manage assigned course details"),
("lms_course_management.material.manage","Manage course materials"),
("lms_course_management.announcement.post","Post course announcements"),
("lms_course_management.assignment.manage","Create and publish assignments"),
("lms_course_management.submission.create","Submit assignment work"),
("lms_course_management.submission.view_course","View course submissions"),
("lms_course_management.grade.manage","Grade submissions"),
("lms_course_management.grade.release","Release grades"),
("lms_course_management.grade.view_self","View own released grades")]
SYSTEM_PERMISSIONS = []
SCOPE_PERMISSIONS = []
ROLE_GRANTS = {
"student":["lms_course_management.course.view","lms_course_management.submission.create","lms_course_management.grade.view_self"],
"faculty":["lms_course_management.course.view","lms_course_management.course.manage","lms_course_management.material.manage","lms_course_management.announcement.post","lms_course_management.assignment.manage","lms_course_management.submission.view_course","lms_course_management.grade.manage","lms_course_management.grade.release"],
"teaching_assistant":["lms_course_management.course.view","lms_course_management.submission.view_course","lms_course_management.grade.manage"],
"observer":["lms_course_management.course.view"]}
