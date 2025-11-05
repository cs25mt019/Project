from django.test import TestCase
from main.models import Teacher, CourseCategory, Course, Student, StudentCourseEnrollment

class TeacherModelTest(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(
            full_name="Ashish Saranshi",
            email="ashish@example.com",
            password="1234",
            qualification="MTech",
            mobile_no="9999999999",
            skills="Django, React"
        )

    def test_teacher_created(self):
        self.assertEqual(self.teacher.full_name, "Ashish Saranshi")
        self.assertTrue(isinstance(self.teacher, Teacher))

class CourseCategoryTest(TestCase):
    def setUp(self):
        self.category = CourseCategory.objects.create(title="Programming", description="Learn code")

    def test_category_created(self):
        self.assertEqual(self.category.title, "Programming")

class StudentEnrollmentTest(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(full_name="Test Teacher", email="teach@test.com", password="123")
        self.student = Student.objects.create(full_name="Ashish", email="ashish@test.com", password="123", username="ashish")
        self.category = CourseCategory.objects.create(title="Tech", description="desc")
        self.course = Course.objects.create(Teacher=self.teacher, category=self.category, title="React", description="Learn React", techs="React")
        self.enroll = StudentCourseEnrollment.objects.create(student=self.student, course=self.course)

    def test_enrollment_exists(self):
        self.assertEqual(self.enroll.student.full_name, "Ashish")
