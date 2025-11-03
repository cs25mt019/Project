from django.urls import path
from . import views

urlpatterns = [
    path('teacher/', views.teacherList.as_view()),
    path('teacher/<int:pk>/', views.teacherDetail.as_view()),
    path('teacher-login', views.teacher_login),

    path('category/', views.CategoryList.as_view()),
    path('course/', views.CourseList.as_view()),

    path('teacher-course/<int:teacher_id>/', views.TeacherCourseList.as_view()),

    path('chapter/', views.ChapterList.as_view()),
    
    #Get/Update/Delete chapter
    path('chapter/<int:pk>/', views.ChapterDetail.as_view()),

    # Course chapters list
    path("course-chapters/<int:course_id>/", views.CourseChapterList.as_view()),

    path("teacher-course-detail/<int:pk>/", views.TeacherCourseDetail.as_view()),
]
