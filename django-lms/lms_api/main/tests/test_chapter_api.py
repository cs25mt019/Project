import pytest
from rest_framework import status
from main.models import Chapter

pytestmark = pytest.mark.django_db


def test_create_chapter(api_client, course):
    data = {
        "course": course.id,
        "title": "Introduction to Django",
        "description": "Basic setup and structure",
        "remarks": "Start here"
    }
    response = api_client.post("/api/chapter/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Chapter.objects.filter(title="Introduction to Django").exists()


def test_list_all_chapters(api_client, chapter):
    response = api_client.get("/api/chapter/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1
    assert any(c["title"] == chapter.title for c in response.data)


def test_get_chapter_detail(api_client, chapter):
    url = f"/api/chapter/{chapter.id}/"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == chapter.title
    assert "description" in response.data


def test_update_chapter(api_client, chapter):
    url = f"/api/chapter/{chapter.id}/"
    response = api_client.patch(url, {"title": "Django Setup"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    chapter.refresh_from_db()
    assert chapter.title == "Django Setup"


def test_delete_chapter(api_client, chapter):
    url = f"/api/chapter/{chapter.id}/"
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Chapter.objects.filter(id=chapter.id).exists()


def test_get_course_chapters(api_client, course, chapter):
    response = api_client.get(f"/api/course-chapters/{course.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1
    assert response.data[0]["course"] == course.id


def test_get_nonexistent_chapter(api_client):
    response = api_client.get("/api/chapter/9999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
