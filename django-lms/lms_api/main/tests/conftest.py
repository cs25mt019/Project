import pytest
from rest_framework.test import APIClient
from main.models import Teacher, Student, CourseCategory, Course, Chapter, StudentCourseEnrollment, CourseRating

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def teacher(db):
    return Teacher.objects.create(
        full_name="Ashish Saranshi",
        email="ashish@test.com",
        password="1234",
        qualification="MTech",
        mobile_no="9999999999",
        skills="Django,React"
    )

@pytest.fixture
def student(db):
    return Student.objects.create(
        full_name="Test Student",
        email="student@test.com",
        password="123",
        username="student123",
        interested_categories="Web,AI"
    )


@pytest.fixture
def category(db):
    return CourseCategory.objects.create(
        title="Web Development",
        description="Courses about building web applications"
    )

@pytest.fixture
def course(db, teacher, category):
    return Course.objects.create(
        Teacher=teacher,
        category=category,
        title="React Mastery",
        description="Learn React step by step",
        techs="React,JavaScript"
    )
@pytest.fixture
def chapter(db, course):
    return Chapter.objects.create(
        course=course,
        title="Introduction to React",
        description="JSX, components, and state",
        remarks="Good start"
    )
@pytest.fixture
def enrollment(db, student, course):
    return StudentCourseEnrollment.objects.create(
        student=student,
        course=course
    )
@pytest.fixture
def course_rating(db, student, course):
    return CourseRating.objects.create(
        student=student,
        course=course,
        rating=4,
        review="Very helpful course"
    )
