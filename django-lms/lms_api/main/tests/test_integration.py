from rest_framework.test import APITestCase
from main.models import Teacher, Student, CourseCategory, Course, StudentCourseEnrollment

class EnrollmentIntegrationTest(APITestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(full_name="Teacher", email="teach@ex.com", password="1234")
        self.student = Student.objects.create(full_name="Ashish", email="ashish@ex.com", password="123", username="ashish")
        self.category = CourseCategory.objects.create(title="Web Dev", description="desc")
        self.course = Course.objects.create(Teacher=self.teacher, category=self.category, title="React", description="JS course", techs="React")

    def test_student_can_enroll_course(self):
        response = self.client.post("/api/student-enroll-course/", {
            "student": self.student.id,
            "course": self.course.id
        })
        self.assertEqual(response.status_code, 201)

    def test_check_enrollment_api(self):
        StudentCourseEnrollment.objects.create(student=self.student, course=self.course)
        response = self.client.get(f"/api/check-enrollment/?student={self.student.id}&course={self.course.id}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['enrolled'])
