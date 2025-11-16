from django.db import models
from django.core import serializers
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone

class Teacher(models.Model):

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    full_name=models.CharField(max_length=100)
    details=models.TextField(null=True)
    email=models.CharField(max_length=100,unique=True)
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

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)



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
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    full_name=models.CharField(max_length=100)
    email=models.CharField(max_length=100,unique=True)
    password=models.CharField(max_length=100)
    username=models.CharField(max_length=50,unique=True)
    interested_categories=models.TextField()
    
    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_"):
            from django.contrib.auth.hashers import make_password
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

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
    


# 7. Assignment and Submissions
class Assignment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='assignments'
    )
    created_by = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='teacher_assignments'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "7. Assignments"

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name='submissions'
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=10, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "8. Assignment Submissions"
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.assignment.title} - {self.student.full_name}"
    
class ChapterProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'chapter')

    def __str__(self):
        return f"{self.student.full_name} - {self.chapter.title}"




#for quiz portal 

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(default=10)  

    # NEW — optional: hard expiry time after quiz starts
    enforce_time = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.quiz.title}"


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.attempt.student.full_name} - {self.question.question_text[:30]}"


#for discussion forum
class Discussion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="discussions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def user_name(self):
        if self.student:
            return self.student.full_name
        elif self.teacher:
            return self.teacher.full_name
        return "Unknown User"

    def __str__(self):
        return f"{self.course.title} - {self.user_name()}"

class FavoriteCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} {self.course.title}"




class PasswordResetOTP(models.Model):
    email = models.CharField(max_length=150)
    otp = models.CharField(max_length=10)
    user_type = models.CharField(max_length=20)  # "student" / "teacher"
    user_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
    used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.email} - {self.otp}"

class LectureNote(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lecture_notes')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="lecture_notes/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Lecture Notes"

    def __str__(self):
        return f"{self.title} ({self.chapter.title})"
