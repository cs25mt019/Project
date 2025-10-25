from rest_framework import serializers
from . import models
class teacherSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Teacher
        fields=["full_name","email","password","qualification","mobile_no","address"]