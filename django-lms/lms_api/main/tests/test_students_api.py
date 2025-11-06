import pytest
from rest_framework import status
from main.models import StudentCourseEnrollment

# Apply Django DB marker to all tests in this file
pytestmark = pytest.mark.django_db


def test_student_list(api_client, student):
    response = api_client.get("/api/student/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1
    assert any(s["email"] == student.email for s in response.data)


def test_student_login_success(api_client, student):
    data = {"username": student.username, "password": student.password}
    response = api_client.post("/api/student/login/", data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["bool"] is True
    assert "student" in response.data


def test_student_login_fail(api_client):
    data = {"username": "wrong", "password": "wrong"}
    response = api_client.post("/api/student/login/", data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["bool"] is False


def test_student_enroll_course(api_client, student, course):
    data = {"student": student.id, "course": course.id}
    response = api_client.post("/api/student-enroll-course/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert StudentCourseEnrollment.objects.filter(student=student, course=course).exists()


def test_check_enrollment_api(api_client, student, course):
    StudentCourseEnrollment.objects.create(student=student, course=course)
    url = f"/api/check-enrollment/?student={student.id}&course={course.id}"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["enrolled"] is True


def test_student_enrolled_courses(api_client, student, course):
    StudentCourseEnrollment.objects.create(student=student, course=course)
    response = api_client.get(f"/api/student-courses/{student.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == course.title


def test_student_course_detail(api_client, course):
    response = api_client.get(f"/api/student-course-detail/{course.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert "course" in response.data
    assert "chapters" in response.data


def test_check_enrollment_missing_params(api_client):
    response = api_client.get("/api/check-enrollment/")
    assert response.status_code == 400
    assert "error" in response.data
