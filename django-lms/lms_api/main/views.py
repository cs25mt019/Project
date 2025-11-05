from django.shortcuts import render
from rest_framework.views import APIView
from .serialize import studentCourseEnrollmentSerializer, teacherSerializer,courseCategorySerializer,courseSerializer,chapterSerializer,studentSerializer,CourseRatingSerializer   
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import models
from .models import Student
from django.db.models import Avg
from rest_framework import status

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
    #permission_classes=[permissions.IsAuthenticated]
class teacherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=teacherSerializer
    #permission_classes=[permissions.IsAuthenticated]
@csrf_exempt
def teacher_login(request):
    email=request.POST['email']
    password=request.POST['password']
    try:
        teacherData=models.Teacher.objects.get(email=email,password=password)
    except models.Teacher.DoesNotExist:
        teacherData=None
    if teacherData:
        return JsonResponse({'bool':True,'teacher_id':teacherData.id})
    else:
        return JsonResponse({'bool':False})

class CategoryList(generics.ListCreateAPIView):
    queryset=models.CourseCategory.objects.all()
    serializer_class=courseCategorySerializer

class CourseList(generics.ListCreateAPIView):
    serializer_class = courseSerializer
    def get_queryset(self):
        qs = models.Course.objects.all()

        category = self.request.GET.get('category')
        skill = self.request.GET.get('skill')   
        teacher = self.request.GET.get('teacher')  

        if category:
            qs = qs.filter(category__title__icontains=category)

        if skill and teacher:
            qs = qs.filter(
                techs__icontains=skill,
                Teacher_id=teacher              
            )
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


class StudentLogin(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            student = Student.objects.get(username=username, password=password)
            data = studentSerializer(student).data
            return Response({"bool": True, "student": data})
        except Student.DoesNotExist:
            return Response({"bool": False, "msg": "Invalid username or password"})


class StudentEnrollCourseList(generics.ListCreateAPIView):
   queryset = models.StudentCourseEnrollment.objects.all()
   serializer_class = studentCourseEnrollmentSerializer

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
    def get(self, request, course_id):
        data = models.CourseRating.objects.filter(course_id=course_id).order_by('-created_at')
        serializer = CourseRatingSerializer(data, many=True)
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
    def post(self, request, teacher_id):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        try:
            teacher = models.Teacher.objects.get(id=teacher_id)
        except models.Teacher.DoesNotExist:
            return Response({"error": "Teacher not found"})

        if teacher.password != old_password:
            return Response({"error": "Old password is incorrect"})

        teacher.password = new_password
        teacher.save()
        return Response({"message": "Password changed successfully"})
    
#teacher Dashboard
class TeacherDashboard(APIView):
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

#for getting all courses a student is enrolled in
class StudentEnrolledCourses(APIView):
    def get(self, request, student_id):
        enrollments = models.StudentCourseEnrollment.objects.filter(student_id=student_id)
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

