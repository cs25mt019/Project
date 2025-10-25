from django.shortcuts import render
from rest_framework.views import APIView
from .serialize import teacherSerializer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from . import models
# class teacherList(APIView):
#     def get(self,request):
#         teachers=models.Teacher.objects.all()
#         serializer=teacherSerializer(teachers,many=True)
#         return Response(serializer.data)
# # Create your views here.

#using generics
class teacherList(generics.ListCreateAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=teacherSerializer
    permission_classes=[permissions.IsAuthenticated]
class teacherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Teacher.objects.all()
    serializer_class=teacherSerializer
    permission_classes=[permissions.IsAuthenticated]