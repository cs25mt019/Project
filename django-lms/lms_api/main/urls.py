from django.urls import path
from . import views
urlpatterns = [
    path('teacher/', views.teacherList.as_view()),
    path('teacher/<int:pk>/', views.teacherDetail.as_view()),
]