from django.db import models
from django.core import serializers

class Teacher(models.Model):
    full_name=models.CharField(max_length=100)
    details=models.TextField(null=True)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    qualification=models.CharField(max_length=200)
    mobile_no=models.CharField(max_length=20)
    skills=models.TextField()
    profile_image = models.ImageField(upload_to="teacher_profile/", null=True, blank=True)

    class Meta:
        verbose_name_plural="1. Teacher"

    def skill_list(self):
        if self.skills:
            return self.skills.split(',')
        return []
class CourseCategory(models.Model):
    title=models.CharField(max_length=150)
    description=models.TextField()

    class Meta:
        verbose_name_plural="2. Course Categories"

    def __str__(self):
        return self.title


class Course(models.Model):
    category=models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    Teacher=models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_courses')
    title=models.CharField(max_length=150)
    description=models.TextField()
    featured_image=models.ImageField(upload_to='course_imgs/', null=True)
    techs=models.TextField(null=True)

    class Meta:
        verbose_name_plural="3. Course"

    def related_videos(self):
        related_videos = Course.objects.filter(
            techs__icontains=self.techs
        ).exclude(id=self.id)[:4]
        return serializers.serialize("json", related_videos)

    def tech_list(self):
        if self.techs:
            return self.techs.split(',')
        return []
    def __str__(self):
        return self.title
    def total_enrolled_students(self):
        total_enrolled_students=StudentCourseEnrollment.objects.filter(course=self).count()
        return total_enrolled_students
        

class Student(models.Model):
    full_name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    username=models.CharField(max_length=50)
    interested_categories=models.TextField()

    def __str__(self):
        return self.full_name
    class Meta:
        verbose_name_plural="4. Student"


class Chapter(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_chapters')
    title=models.CharField(max_length=150)
    description=models.TextField()
    video=models.FileField(upload_to='chapter_videos/', null=True)
    remarks=models.TextField(null=True)

    class Meta:
        verbose_name_plural="5. Chapter"

class StudentCourseEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "6. Student Course Enrollment"
        unique_together = ('student', 'course')
    def __str__(self):
        return f"{self.course}-{self.student}"
    
class CourseRating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=1)  # 1–5
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # student can rate only once

    def __str__(self):
        return f"{self.student} rated {self.course} - {self.rating}"