from django.shortcuts import render
from rest_framework.views import APIView
from .serialize import teacherSerializer,courseCategorySerializer,courseSerializer,chapterSerializer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import models

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
