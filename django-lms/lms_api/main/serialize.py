from rest_framework import serializers
from . import models
class teacherSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Teacher
        fields=["id","full_name","email","password","qualification","mobile_no","skills"]

class courseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=models.CourseCategory
        fields=["id","title","description"]

class courseSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Course
        fields=["id","category","Teacher","title","description","featured_image","techs"]   

class chapterSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Chapter
        fields=["id","course","title","description","video","remarks"]  
        