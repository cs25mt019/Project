import pytest
from rest_framework import status
from main.models import Teacher

@pytest.mark.django_db
def test_teacher_list(api_client, teacher):
    response = api_client.get("/api/teacher/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1
    assert any(t["full_name"] == teacher.full_name for t in response.data)


@pytest.mark.django_db
def test_teacher_detail(api_client, teacher):
    url = f"/api/teacher/{teacher.id}/"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["full_name"] == teacher.full_name


@pytest.mark.django_db
def test_teacher_create(api_client):
    data = {
        "full_name": "John Doe",
        "details": "Backend Developer",
        "email": "john@test.com",
        "password": "pass123",
        "qualification": "BTech",
        "mobile_no": "8888888888",
        "skills": "Python,Django"
    }
    response = api_client.post("/api/teacher/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Teacher.objects.filter(email="john@test.com").exists()


@pytest.mark.django_db
def test_teacher_update(api_client, teacher):
    url = f"/api/teacher/{teacher.id}/"
    response = api_client.patch(url, {"qualification": "PhD"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    teacher.refresh_from_db()
    assert teacher.qualification == "PhD"


@pytest.mark.django_db
def test_teacher_delete(api_client, teacher):
    url = f"/api/teacher/{teacher.id}/"
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Teacher.objects.filter(id=teacher.id).exists()


@pytest.mark.django_db
def test_teacher_login_success(api_client, teacher):
    data = {"email": teacher.email, "password": teacher.password}
    response = api_client.post("/api/teacher-login", data)
    json_data = response.json() 
    assert response.status_code == 200
    assert json_data["bool"] is True
    assert "teacher_id" in json_data


@pytest.mark.django_db
def test_teacher_login_fail(api_client):
    data = {"email": "wrong@test.com", "password": "wrongpass"}
    response = api_client.post("/api/teacher-login", data)
    json_data = response.json()
    assert response.status_code == 200
    assert json_data["bool"] is False

