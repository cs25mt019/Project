from django.urls import path
from . import views

urlpatterns = [
    path('teacher/', views.teacherList.as_view()),
    path('teacher/<int:pk>/', views.teacherDetail.as_view()),
    path('teacher-login', views.teacher_login),

    path('category/', views.CategoryList.as_view()),
    path('course/', views.CourseList.as_view()),
    path('course/<int:pk>/', views.CourseDetail.as_view()),
    path('teacher-course/<int:teacher_id>/', views.TeacherCourseList.as_view()),

    path('chapter/', views.ChapterList.as_view()),
    
    #Get/Update/Delete chapter
    path('chapter/<int:pk>/', views.ChapterDetail.as_view()),

    # Course chapters list
    path("course-chapters/<int:course_id>/", views.CourseChapterList.as_view()),

    path("teacher-course-detail/<int:pk>/", views.TeacherCourseDetail.as_view()),

    path('student/', views.StudentList.as_view()),
     path("student/login/", views.StudentLogin.as_view()),
    
   path('student-enroll-course/', views.StudentEnrollCourseList.as_view()),
    path('fetch-enrolled-students/<int:course_id>/', views.EnrolledStudentsList.as_view()),
    path('check-enrollment/', views.CheckEnrollmentAPI.as_view(), name='check-enrollment'),
    #review and rating paths
    path('rate-course/', views.CourseRatingView.as_view(), name='rate-course'),
    path('course-rating/<int:course_id>/', views.CourseAverageRating.as_view(), name='course-rating'),
    path("course-reviews/<int:course_id>/", views.CourseReviews.as_view()),
    path("delete-review/<int:id>/", views.DeleteReview.as_view()),
    #for getting all students of a teacher's courses
    path("teacher-students/<int:teacher_id>/", views.TeacherStudents.as_view()),
    #teacher change password
    path("teacher-change-password/<int:teacher_id>/", views.TeacherChangePassword.as_view()),
    #teacher dashboard data
    path("teacher-dashboard/<int:teacher_id>/", views.TeacherDashboard.as_view(), name="teacher-dashboard"),
      
    #student enrolled courses
    path('student-courses/<int:student_id>/', views.StudentEnrolledCourses.as_view(), name='student-courses'),

    # Student course detail with chapters
    path('student-course-detail/<int:course_id>/', views.StudentCourseDetail.as_view(), name='student-course-detail'),
]
