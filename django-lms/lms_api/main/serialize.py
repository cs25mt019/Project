from rest_framework import serializers
from django.db.models import Avg
from . import models
class teacherSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Teacher
        fields=["id","full_name","details","email","password","qualification","mobile_no","skills","teacher_courses","skill_list","profile_image"]
        depth=1

class courseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=models.CourseCategory
        fields=["id","title","description"]

class courseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=models.CourseCategory.objects.all())
    
    # Show teacher nested details 
    Teacher = teacherSerializer(read_only=True)

    # Still allow POST/PUT by teacher_id
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Teacher.objects.all(),
        source='Teacher',
        write_only=True
    )
    average_rating = serializers.SerializerMethodField() 

    def get_average_rating(self, obj):
        avg = models.CourseRating.objects.filter(course=obj).aggregate(avg_rating=Avg('rating'))
        return round(avg['avg_rating'] or 0, 1)
    

    class Meta:
        model = models.Course
        fields = [
            "id", "category", "teacher_id", "Teacher",
            "title", "description", "featured_image",
            "techs", "course_chapters", "related_videos",
            "tech_list", "total_enrolled_students","average_rating"  
        ]
        depth = 1


class chapterSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Chapter
        fields=["id","course","title","description","video","remarks"]  

class studentSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Student
        fields=["id","full_name","email","password","username","interested_categories"]

class studentCourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.StudentCourseEnrollment
        fields=["id","student","course","enrollment_date"]  
    
class CourseRatingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)

    class Meta:
        model = models.CourseRating
        fields = [
            'id', 'student', 'student_name', 'course',
            'rating', 'review', 'created_at'
        ]
