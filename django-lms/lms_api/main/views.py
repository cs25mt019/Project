from django.shortcuts import render
from rest_framework.views import APIView
from .serialize import studentCourseEnrollmentSerializer,LectureNoteSerializer,FavoriteCourseSerializer, teacherSerializer,courseCategorySerializer,courseSerializer,chapterSerializer,studentSerializer,CourseRatingSerializer,AssignmentSerializer, AssignmentSubmissionSerializer , DiscussionSerializer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import models
from .models import Student
from django.db.models import Avg
import json
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
from .custom_auth import CustomJWTAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

# class teacherList(APIView):
#     def get(self,request):
#         teachers=models.Teacher.objects.all()
#         serializer=teacherSerializer(teachers,many=True)
#         return Response(serializer.data)
# # Create your views here.

#using generics
class teacherList(generics.ListCreateAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=teacherSerializer
    permission_classes=[AllowAny]
    #permission_classes=[permissions.IsAuthenticated]
class teacherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=teacherSerializer
    #permission_classes=[permissions.IsAuthenticated]
@csrf_exempt
def teacher_login(request):
    """
    Expect JSON body: {"email": "x@x.com", "password": "secret"}
    Returns: {"bool": True, "teacher_id": id} on success
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return JsonResponse({"error": "email and password are required"}, status=400)

    try:
        teacher = models.Teacher.objects.get(email=email)
    except models.Teacher.DoesNotExist:
        return JsonResponse({"bool": False, "msg": "Invalid credentials"}, status=401)

    if check_password(password, teacher.password):
        return JsonResponse({"bool": True, "teacher_id": teacher.id})
    return JsonResponse({"bool": False, "msg": "Invalid credentials"}, status=401)

class CategoryList(generics.ListCreateAPIView):
    queryset=models.CourseCategory.objects.all()
    serializer_class=courseCategorySerializer
    permission_classes=[AllowAny]

class CourseList(generics.ListCreateAPIView):
    serializer_class = courseSerializer
    permission_classes=[AllowAny]

    def get_queryset(self):
        qs = models.Course.objects.all()
        category = self.request.GET.get('category')
        skill = self.request.GET.get('skill')
        teacher = self.request.GET.get('teacher')

        if category:
            qs = qs.filter(category__title__icontains=category)
        if skill:
            qs = qs.filter(techs__icontains=skill)
        if teacher:
            qs = qs.filter(Teacher_id=teacher)
        return qs

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Course.objects.all()
    serializer_class=courseSerializer
#specific course by teacher id
class TeacherCourseList(generics.ListCreateAPIView):
    serializer_class=courseSerializer

    def get_queryset(self):
        teacher_id=self.kwargs['teacher_id']
        return models.Course.objects.filter(Teacher=teacher_id)
    
class TeacherCourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Course.objects.all()
    serializer_class=courseSerializer
    
class ChapterList(generics.ListCreateAPIView):
    queryset=models.Chapter.objects.all()
    serializer_class=chapterSerializer
    
class CourseChapterList(generics.ListAPIView):
    serializer_class=chapterSerializer

    def get_queryset(self):
        course_id=self.kwargs['course_id']
        course=models.Course.objects.get(pk=course_id)
        return models.Chapter.objects.filter(course=course)

#used to retrieve specific chapter within a course
class CourseChapterDetail(generics.RetrieveAPIView):
    serializer_class = chapterSerializer

    def get_object(self):
        course_id = self.kwargs['course_id']
        chapter_id = self.kwargs['chapter_id']
        return models.Chapter.objects.get(course_id=course_id, id=chapter_id)

class ChapterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Chapter.objects.all()
    serializer_class=chapterSerializer



#student data
class StudentList(generics.ListCreateAPIView):
    queryset=models.Student.objects.all()
    serializer_class=studentSerializer
    permission_classes=[AllowAny]


class StudentLogin(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            student = Student.objects.get(username=username)
            if check_password(password, student.password):
                data = studentSerializer(student).data
                return Response({"bool": True, "student": data})
        except Student.DoesNotExist:
            pass
        return Response({"bool": False, "msg": "Invalid username or password"})



class StudentEnrollCourseList(generics.ListCreateAPIView):
   queryset = models.StudentCourseEnrollment.objects.all()
   serializer_class = studentCourseEnrollmentSerializer
   permission_classes = [IsAuthenticated]

class EnrolledStudentsList(generics.ListAPIView):
    serializer_class = studentSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        enrollments = models.StudentCourseEnrollment.objects.filter(course_id=course_id)
        student_ids = enrollments.values_list('student_id', flat=True)
        return models.Student.objects.filter(id__in=student_ids)
    
class CheckEnrollmentAPI(APIView):
    def get(self, request, format=None):
        student_id = request.GET.get("student")
        course_id = request.GET.get("course")

        if not student_id or not course_id:
            return Response(
                {"error": "student and course parameters are required"},
                status=400
            )

        is_enrolled = models.StudentCourseEnrollment.objects.filter(
            student_id=student_id, course_id=course_id
        ).exists()

        return Response({"enrolled": is_enrolled}, status=200)
    
class CourseRatingView(APIView):
    def post(self, request, format=None):
        student = request.data.get("student")
        course = request.data.get("course")
        rating = request.data.get("rating")
        review = request.data.get("review")

        existing = models.CourseRating.objects.filter(student_id=student, course_id=course).first()

        if existing:
            existing.rating = rating
            existing.review = review
            existing.save()
            return Response({"message": "Rating updated"}, status=200)

        serializer = CourseRatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Rating submitted"}, status=201)

        return Response(serializer.errors, status=400)

class CourseAverageRating(APIView):
    def get(self, request, course_id, format=None):
        avg = models.CourseRating.objects.filter(course_id=course_id).aggregate(avg_rating=Avg('rating'))
        return Response({"average_rating": avg['avg_rating'] or 0})
class CourseReviews(APIView):
    permission_classes = [AllowAny]  # or IsAuthenticated if you require login

    def get(self, request, course_id):
        qs = models.CourseRating.objects.filter(course_id=course_id).order_by('-created_at')
        serializer = CourseRatingSerializer(qs, many=True)
        return Response(serializer.data)

class DeleteReview(APIView):
    def delete(self, request, id):
        review = models.CourseRating.objects.filter(id=id).first()
        if review:
            review.delete()
            return Response({"message": "Review deleted"})
        return Response({"error": "Review not found"}, status=404)

class TeacherStudents(APIView):
    def get(self, request, teacher_id):
        # get all course IDs created by this teacher
        course_ids = models.Course.objects.filter(Teacher_id=teacher_id).values_list('id', flat=True)

        # get student IDs enrolled in those courses
        student_ids = models.StudentCourseEnrollment.objects.filter(
            course_id__in=course_ids
        ).values_list('student_id', flat=True).distinct()

        # fetch student objects
        students = models.Student.objects.filter(id__in=student_ids)
        serializer = studentSerializer(students, many=True)
        return Response(serializer.data)


class TeacherChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, teacher_id):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"error": "old_password and new_password are required"}, status=400)

        try:
            teacher = models.Teacher.objects.get(id=teacher_id)
        except models.Teacher.DoesNotExist:
            return Response({"error": "Teacher not found"}, status=404)

        if not check_password(old_password, teacher.password):
            return Response({"error": "Old password is incorrect"}, status=400)

        teacher.password = make_password(new_password)
        teacher.save()
        return Response({"message": "Password changed successfully"}, status=200)
    
#teacher Dashboard
class TeacherDashboard(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, teacher_id):
        # Total courses by teacher
        total_courses = models.Course.objects.filter(Teacher_id=teacher_id).count()

        # Total students across all teacher's courses
        total_students = models.StudentCourseEnrollment.objects.filter(
            course__Teacher_id=teacher_id
        ).values("student").distinct().count()

        # Average rating across teacher’s courses
        avg_rating = models.CourseRating.objects.filter(
            course__Teacher_id=teacher_id
        ).aggregate(Avg("rating"))["rating__avg"] or 0

        return Response({
            "total_courses": total_courses,
            "total_students": total_students,
            "avg_rating": round(avg_rating, 2),
        })
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import StudentCourseEnrollment
from .serialize import courseSerializer


class StudentEnrolledCourses(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        # Using the authenticated user (from token)
        user_id = request.user.id
        enrollments = StudentCourseEnrollment.objects.filter(student_id=user_id)
        courses = [enrollment.course for enrollment in enrollments]
        serializer = courseSerializer(courses, many=True)
        return Response(serializer.data)

#course detail along with its chapters for students
class StudentCourseDetail(APIView):
    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(pk=course_id)
        except models.Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)

        course_data = courseSerializer(course).data
        chapters = models.Chapter.objects.filter(course=course)
        chapter_data = chapterSerializer(chapters, many=True).data

        return Response({
            "course": course_data,
            "chapters": chapter_data
        })


# Teacher creates and views assignments for their courses
class AssignmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        teacher_id = self.request.query_params.get('teacher')
        course_id = self.request.query_params.get('course')

        queryset = models.Assignment.objects.all()
        if teacher_id:
            queryset = queryset.filter(created_by_id=teacher_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.order_by('-created_at')


# Retrieve / Update / Delete a specific assignment
class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Assignment.objects.all()
    serializer_class = AssignmentSerializer


# Student submits assignment
class AssignmentSubmissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSubmissionSerializer

    def get_queryset(self):
        assignment_id = self.request.query_params.get('assignment')
        student_id = self.request.query_params.get('student')

        queryset = models.AssignmentSubmission.objects.all()
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        return queryset.order_by('-submitted_at')


# Retrieve / Update / Delete submission
class AssignmentSubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer

class CourseAssignmentsList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return models.Assignment.objects.filter(course_id=course_id).order_by("-id")


class AssignmentSubmissionsList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    """Return all student submissions for a specific assignment"""
    serializer_class = AssignmentSubmissionSerializer

    def get_queryset(self):
        assignment_id = self.kwargs["assignment_id"]
        return models.AssignmentSubmission.objects.filter(assignment_id=assignment_id).order_by("-submitted_at")
    
class GradeSubmission(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    """Allows teacher to update grade and feedback for a student submission"""
    queryset = models.AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer

class ChapterProgressView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        student_id = request.data.get("student")
        chapter_id = request.data.get("chapter")

        if not student_id or not chapter_id:
            return Response({"error": "student and chapter required"}, status=400)

        progress, created = models.ChapterProgress.objects.get_or_create(
            student_id=student_id, chapter_id=chapter_id
        )
        progress.completed = True
        progress.save()

        return Response({"message": "Progress updated"})

class StudentCourseProgress(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, student_id, course_id):
        total_chapters = models.Chapter.objects.filter(course_id=course_id).count()
        completed_chapters = models.ChapterProgress.objects.filter(
            student_id=student_id, chapter__course_id=course_id, completed=True
        ).count()

        progress_percent = (
            (completed_chapters / total_chapters) * 100 if total_chapters > 0 else 0
        )
        return Response({
            "total_chapters": total_chapters,
            "completed": completed_chapters,
            "progress": round(progress_percent, 1)
        })

from rest_framework import generics, status
from rest_framework.response import Response
from .models import Quiz, Question, QuizAttempt, StudentAnswer
from .serialize import QuizSerializer, QuestionSerializer, QuizAttemptSerializer, StudentAnswerSerializer

# Teacher adds and views quizzes per course
class QuizListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        return Quiz.objects.filter(course_id=course_id).order_by('-id')


# view or delete a specific quiz
class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


# Add questions to a quiz
class QuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        quiz_id = self.request.query_params.get('quiz')
        return Question.objects.filter(quiz_id=quiz_id)


# Student attempts quiz
# Student can submit AND view quiz attempts
class QuizAttemptListCreateView(generics.ListCreateAPIView):
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        queryset = QuizAttempt.objects.all()
        student_id = self.request.query_params.get("student")
        quiz_id = self.request.query_params.get("quiz")

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)

     
        return queryset.order_by("-submitted_at")

    def create(self, request, *args, **kwargs):
        student = request.data.get("student")
        quiz = request.data.get("quiz")
        answers = request.data.get("answers", [])

        if not student or not quiz:
            return Response({"error": "Missing student or quiz ID"}, status=status.HTTP_400_BAD_REQUEST)

        # 1️⃣ CHECK FOR EXISTING ATTEMPT (quiz start time)
        try:
            attempt = QuizAttempt.objects.get(
                quiz_id=quiz,
                student_id=student,
                completed=False
            )
        except QuizAttempt.DoesNotExist:
            return Response({"error": "Attempt not found or expired"}, status=status.HTTP_400_BAD_REQUEST)

        # 2️⃣ CHECK IF TIME IS OVER
        quiz_obj = attempt.quiz
        allowed_seconds = quiz_obj.duration_minutes * 60

        elapsed_seconds = (timezone.now() - attempt.started_at).total_seconds()

        if quiz_obj.enforce_time and elapsed_seconds > allowed_seconds:
            # Force end + block submission
            attempt.completed = True
            attempt.ended_at = timezone.now()
            attempt.score = 0
            attempt.save()

            return Response(
                {"error": "Time is over. Your quiz was auto-submitted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3️⃣ NORMAL SCORING
        total_questions = len(answers)
        correct_answers = 0

        for ans in answers:
            try:
                question = Question.objects.get(id=ans["question"])
                if ans["selected_option"] == question.correct_option:
                    correct_answers += 1
            except Question.DoesNotExist:
                continue

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        # 4️⃣ UPDATE THE EXISTING ATTEMPT (not create new)
        attempt.score = score
        attempt.completed = True
        attempt.ended_at = timezone.now()
        attempt.save()

        # 5️⃣ SAVE STUDENT ANSWERS
        for ans in answers:
            StudentAnswer.objects.create(
                attempt=attempt,
                question_id=ans["question"],
                selected_option=ans["selected_option"],
            )

        return Response(
            {
                "message": "Quiz submitted successfully",
                "score": score,
                "time_taken_seconds": elapsed_seconds
            },
            status=status.HTTP_200_OK,
        )


# List all attempts for a given quiz (for teacher view)
class QuizAttemptsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        quiz_id = self.kwargs["quiz_id"]
        return QuizAttempt.objects.filter(quiz_id=quiz_id).select_related("student").order_by("-submitted_at")



class DiscussionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DiscussionSerializer

    def get_queryset(self):
        course_id = self.request.query_params.get("course")
        return models.Discussion.objects.filter(course_id=course_id).order_by("-created_at")


from django.db.models import Q

class GlobalSearchView(APIView):
    """
    Search for Courses or Teachers globally
    Example: /api/search/?q=python
    """
    permission_classes = [AllowAny]
    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Response({"courses": [], "teachers": []})

        # Search Courses
        courses = models.Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(techs__icontains=query)
        )

        # Search Teachers
        teachers = models.Teacher.objects.filter(
            Q(full_name__icontains=query) |
            Q(skills__icontains=query)
        )

        course_data = courseSerializer(courses, many=True).data
        teacher_data = teacherSerializer(teachers, many=True).data

        return Response({
            "courses": course_data,
            "teachers": teacher_data
        })
    
class HomePageView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        from django.db.models import Count

        popular_courses = (
            models.Course.objects.annotate(num_students=Count("studentcourseenrollment"))
            .order_by("-num_students")[:4]
        )
        latest_courses = models.Course.objects.order_by("-id")[:4]
        popular_teachers = (
            models.Teacher.objects.annotate(
                total_students=Count("teacher_courses__studentcourseenrollment", distinct=True)
            )
            .order_by("-total_students")[:4]
        )

        data = {
            "popular_courses": courseSerializer(popular_courses, many=True).data,
            "latest_courses": courseSerializer(latest_courses, many=True).data,
            "popular_teachers": teacherSerializer(popular_teachers, many=True).data,
        }
        return Response(data)

class FavoriteCourseListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteCourseSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return models.FavoriteCourse.objects.filter(student_id=student_id).order_by('-added_at')

class RemoveFavoriteCourse(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, student_id, course_id):
        fav = models.FavoriteCourse.objects.filter(student_id=student_id, course_id=course_id).first()
        if fav:
            fav.delete()
            return Response({"message": "Removed from favorites"})
        return Response({"error": "Favorite not found"}, status=404)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_favorite(request):
    student = request.GET.get("student")
    course = request.GET.get("course")

    exists = models.FavoriteCourse.objects.filter(
        student_id=student,
        course_id=course
    ).exists()

    return Response({"is_favorite": exists})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite(request):
    student = request.data.get("student")
    course = request.data.get("course")

    exists = models.FavoriteCourse.objects.filter(
        student_id=student, course_id=course
    ).exists()

    if exists:
        return Response({"message": "Already in favorites"}, status=200)

    models.FavoriteCourse.objects.create(student_id=student, course_id=course)
    return Response({"message": "Added to favorites"}, status=201)

@api_view(['DELETE'])
def remove_favorite(request):
    student = request.GET.get('student')
    course = request.GET.get('course')

    fav = models.FavoriteCourse.objects.filter(student_id=student, course_id=course).first()
    if fav:
        fav.delete()
        return Response({"message": "Removed from favorites"}, status=200)

    return Response({"error": "Not found"}, status=404)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework import status

class StudentChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        old_pw = request.data.get("old_password")
        new_pw = request.data.get("new_password")

        try:
            student = models.Student.objects.get(id=student_id)
        except models.Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        # Verify old password
        if not check_password(old_pw, student.password):
            return Response({"error": "Incorrect old password"}, status=400)

        # Set new password correctly
        student.password = make_password(new_pw)
        student.save()

        return Response({"message": "Password updated successfully"}, status=200)

class LectureNoteListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LectureNoteSerializer

    def get_queryset(self):
        chapter_id = self.request.query_params.get("chapter")
        if not chapter_id:
            return models.LectureNote.objects.none()
        return models.LectureNote.objects.filter(chapter_id=chapter_id).order_by("-uploaded_at")

class LectureNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.LectureNote.objects.all()
    serializer_class = LectureNoteSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Student
from .serialize import courseSerializer
from .utils.recommender import recommend_courses_for_student

class RecommendedCourses(APIView):
    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        recommended = recommend_courses_for_student(student)

        serialized = courseSerializer(recommended, many=True)
        return Response(serialized.data, status=200)

from rest_framework import generics
from .models import Student
from .serialize import studentSerializer

class StudentDetail(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = studentSerializer
class StartQuizView(APIView):
    def post(self, request):
        quiz_id = request.data.get("quiz")
        student_id = request.data.get("student")

        # 1CHECK IF STUDENT ALREADY COMPLETED THE QUIZ
        completed_attempt = QuizAttempt.objects.filter(
            quiz_id=quiz_id,
            student_id=student_id,
            completed=True
        ).first()

        if completed_attempt:
            return Response(
                {
                    "already_attempted": True,
                    "score": completed_attempt.score,
                    "submitted_at": completed_attempt.submitted_at,
                },
                status=200
            )

        # 2CHECK IF STUDENT HAS AN ACTIVE (NOT FINISHED) ATTEMPT
        active_attempt = QuizAttempt.objects.filter(
            quiz_id=quiz_id,
            student_id=student_id,
            completed=False
        ).first()

        if active_attempt:
            return Response(
                {
                    "attempt_id": active_attempt.id,
                    "started_at": active_attempt.started_at,
                    "already_attempted": False
                },
                status=200
            )

        # 3NO ATTEMPT EXISTS → CREATE FIRST ATTEMPT
        new_attempt = QuizAttempt.objects.create(
            quiz_id=quiz_id,
            student_id=student_id,
        )

        return Response(
            {
                "attempt_id": new_attempt.id,
                "started_at": new_attempt.started_at,
                "already_attempted": False
            },
            status=200
        )



