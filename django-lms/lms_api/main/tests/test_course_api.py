import pytest
from rest_framework import status
from main.models import Course

pytestmark = pytest.mark.django_db


def test_create_course(api_client, teacher, category):
    data = {
        "teacher_id": teacher.id,
        "category": category.id,
        "title": "Advanced Django",
        "description": "Deep dive into Django backend",
        "techs": "Django,Python"
    }
    response = api_client.post("/api/course/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Course.objects.filter(title="Advanced Django").exists()


def test_list_all_courses(api_client, course):
    response = api_client.get("/api/course/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1
    assert any(c["title"] == course.title for c in response.data)


def test_get_course_detail(api_client, course):
    url = f"/api/course/{course.id}/"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == course.title
    assert "Teacher" in response.data


def test_update_course(api_client, course):
    url = f"/api/course/{course.id}/"
    response = api_client.patch(url, {"title": "React Mastery Updated"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    course.refresh_from_db()
    assert course.title == "React Mastery Updated"


def test_delete_course(api_client, course):
    url = f"/api/course/{course.id}/"
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Course.objects.filter(id=course.id).exists()


def test_filter_courses_by_category(api_client, category, teacher):
    Course.objects.create(
        Teacher=teacher,
        category=category,
        title="Web Dev 101",
        description="Intro course",
        techs="HTML,CSS"
    )
    response = api_client.get(f"/api/course/?category={category.title}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1
    # verify returned course has correct category id
    assert all(c["category"] == category.id for c in response.data)



def test_filter_courses_by_skill_and_teacher(api_client, teacher, category):
    Course.objects.create(
        Teacher=teacher,
        category=category,
        title="React for Beginners",
        description="Frontend framework",
        techs="React"
    )
    url = f"/api/course/?skill=React&teacher={teacher.id}"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert all("React" in c["techs"] for c in response.data)


def test_teacher_course_list(api_client, teacher, course):
    response = api_client.get(f"/api/teacher-course/{teacher.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert any(c["title"] == course.title for c in response.data)
