from rest_framework.test import APITestCase
from rest_framework import status
from main.models import Teacher, CourseCategory, Course, Student

class CourseApiTest(APITestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(full_name="Test Teacher", email="teach@test.com", password="123")
        self.category = CourseCategory.objects.create(title="Backend", description="Learn backend")

    def test_create_course(self):
        data = {
            "teacher_id": self.teacher.id,
            "category": self.category.id,
            "title": "Django Basics",
            "description": "Learn Django",
            "techs": "Python, Django"
        }
        response = self.client.post("/api/course/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_courses(self):
        response = self.client.get("/api/course/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
