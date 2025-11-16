from django.urls import path
from . import views
from . import auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


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

   # path('student/', views.StudentList.as_view()),
    # path("student/login/", views.StudentLogin.as_view()),
    
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

    #assignments
    path('assignments/', views.AssignmentListCreateView.as_view(), name='assignments'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment-detail'),

    # Submissions
    path('submissions/', views.AssignmentSubmissionListCreateView.as_view(), name='submissions'),
    path('submissions/<int:pk>/', views.AssignmentSubmissionDetailView.as_view(), name='submission-detail'),

    path("course-assignments/<int:course_id>/", views.CourseAssignmentsList.as_view()),

    path("assignment-submissions/<int:assignment_id>/", views.AssignmentSubmissionsList.as_view()),

    path("grade-submission/<int:pk>/", views.GradeSubmission.as_view()),

    path("chapter-progress/", views.ChapterProgressView.as_view()),

    path("course-progress/<int:student_id>/<int:course_id>/", views.StudentCourseProgress.as_view()),

    #for quizes
    path("quizzes/", views.QuizListCreateView.as_view(), name="quiz-list-create"),
    path("quizzes/<int:pk>/", views.QuizDetailView.as_view(), name="quiz-detail"),
    path("questions/", views.QuestionListCreateView.as_view(), name="question-list-create"),
    path("quiz-attempts/", views.QuizAttemptListCreateView.as_view(), name="quiz_attempts"),

    #for teacher to check result
    path("quiz/<int:quiz_id>/attempts/", views.QuizAttemptsListView.as_view(), name="quiz-attempts-list"),

    path("discussions/", views.DiscussionListCreateView.as_view(), name="discussions"),
    
    #for searching
    path("search/", views.GlobalSearchView.as_view(), name="global-search"),

    path("home/", views.HomePageView.as_view(), name="home"),

     path("auth/student/register/", auth_views.StudentRegisterView.as_view(), name="student-register"),
    path("auth/student/login/", auth_views.StudentLoginView.as_view(), name="student-login"),

    # Teacher Auth
    path("auth/teacher/register/", auth_views.TeacherRegisterView.as_view(), name="teacher-register"),
    path("auth/teacher/login/", auth_views.TeacherLoginView.as_view(), name="teacher-login"),

    # Common Logout
    path("auth/logout/", auth_views.LogoutView.as_view(), name="logout"),

    #path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('favorites/<int:student_id>/', views.FavoriteCourseListCreateView.as_view()),
    path('favorites/remove/<int:student_id>/<int:course_id>/', views.RemoveFavoriteCourse.as_view()),
    path("check-favorite/", views.check_favorite, name="check_favorite"),
    path("add-favorite/", views.add_favorite, name="add_favorite"),
    path("remove-favorite/", views.remove_favorite, name="remove_favorite"),
    path("student-change-password/<int:student_id>/", views.StudentChangePasswordView.as_view()),

    path("auth/request-reset-otp/", auth_views.RequestResetOTP.as_view()),
    path("auth/verify-reset-otp/", auth_views.VerifyResetOTP.as_view()),
    path("auth/reset-password/", auth_views.ResetPassword.as_view()),

    # Lecture Notes
path("lecture-notes/", views.LectureNoteListCreateView.as_view()),
path("lecture-notes/<int:pk>/", views.LectureNoteDetailView.as_view()),

path("recommended-courses/<int:student_id>/", views.RecommendedCourses.as_view()),
path("student/<int:pk>/", views.StudentDetail.as_view()),
path("start-quiz/", views.StartQuizView.as_view(), name="start-quiz"),


]
