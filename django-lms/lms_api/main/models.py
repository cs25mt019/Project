from django.db import models

# Create your models here.
class Teacher(models.Model):
    full_name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    qualification=models.CharField(max_length=200)
    mobile_no=models.CharField(max_length=20)
    skills=models.TextField()
    class Meta:
        verbose_name_plural="1. Teacher"
    

#course category model
class CourseCategory(models.Model):
    title=models.CharField(max_length=150)
    description=models.TextField()

    class Meta:
        verbose_name_plural="2. Course Categories"
    def __str__(self):
        return self.title
#course Model
class Course(models.Model):
    category=models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    Teacher=models.ForeignKey(Teacher, on_delete=models.CASCADE)
    title=models.CharField(max_length=150)
    description =models.TextField()
    featured_image=models.ImageField(upload_to='course_imgs/',null=True)
    techs=models.TextField(null=True)

    class Meta:
        verbose_name_plural="3. Course"

#Teachers Model
class Student(models.Model):
    full_name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    qualification=models.CharField(max_length=200)
    mobile_no=models.CharField(max_length=20)
    address=models.TextField()
    interested_categories=models.TextField()
    class Meta:
        verbose_name_plural="4. Student"

#Chapter Model
class Chapter(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE)
    title=models.CharField(max_length=150)
    description=models.TextField()
    video=models.FileField(upload_to='chapter_videos/',null=True)
    remarks=models.TextField(null=True)

    class Meta:
        verbose_name_plural="5. Chapter"