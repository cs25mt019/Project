from rest_framework import serializers
from django.db.models import Avg
from . import models
from django.contrib.auth.hashers import make_password
class teacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields=[
            "id","full_name","details","email","password","qualification",
            "mobile_no","skills","teacher_courses","skill_list","profile_image"
        ]
        depth=1
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If password present, hash it
        pwd = validated_data.get("password", None)
        if pwd:
            validated_data["password"] = make_password(pwd)
        return super().update(instance, validated_data)


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
        extra_kwargs = {
            "password": {"write_only": True}  
        }
        read_only_fields = ["email"]

    # def create(self, validated_data):
    #     from django.contrib.auth.hashers import make_password
    #     validated_data["password"] = make_password(validated_data["password"])
    #     return super().create(validated_data)

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


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Assignment
        fields = '__all__'

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)

    class Meta:
        model = models.AssignmentSubmission
        fields = [
            "id", "assignment", "assignment_title",
            "student", "student_name",
            "submitted_file", "submitted_at",
            "grade", "feedback",
        ]

class ChapterProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChapterProgress
        fields = ['id', 'student', 'chapter', 'completed', 'completed_at']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Question
        fields = '__all__'


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = models.Quiz
        fields = '__all__'


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentAnswer
        fields = '__all__'


class StudentMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Student
        fields = ["id", "full_name", "email"]

class QuizAttemptSerializer(serializers.ModelSerializer):
    student = StudentMiniSerializer(read_only=True)
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = models.QuizAttempt
        fields = [
            "id",
            "student",  # now returns full student data
            "quiz",
            "score",
            "completed",
            "submitted_at",
            "formatted_date",
        ]

    def get_formatted_date(self, obj):
        if obj.submitted_at:
            return obj.submitted_at.strftime("%b %d, %Y %I:%M %p")  # Example: Nov 09, 2025 06:35 PM
        return None


class DiscussionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Discussion
        fields = ["id", "course", "student", "teacher", "content", "created_at", "user_name"]

    def get_user_name(self, obj):
        return obj.user_name()


class FavoriteCourseSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    teacher_id = serializers.IntegerField(source="course.Teacher.id", read_only=True)
    teacher_name = serializers.CharField(source="course.Teacher.full_name", read_only=True)

    class Meta:
        model = models.FavoriteCourse
        fields = [
            "id",
            "course",
            "course_title",
            "teacher_id",
            "teacher_name",
            "added_at",
        ]

class LectureNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LectureNote
        fields = "__all__"
