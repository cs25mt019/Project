import pytest
from rest_framework import status
from main.models import CourseCategory

pytestmark = pytest.mark.django_db


def test_create_category(api_client):
    data = {"title": "AI", "description": "Artificial Intelligence courses"}
    response = api_client.post("/api/category/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert CourseCategory.objects.filter(title="AI").exists()


def test_list_categories(api_client):
    CourseCategory.objects.create(title="Machine Learning", description="ML basics")
    CourseCategory.objects.create(title="Web Development", description="Frontend and backend")
    response = api_client.get("/api/category/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2
    titles = [cat["title"] for cat in response.data]
    assert "Machine Learning" in titles


def test_category_string_representation(db):
    category = CourseCategory.objects.create(title="DevOps", description="Cloud infra")
    assert str(category) == "DevOps"
