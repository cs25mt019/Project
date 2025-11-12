from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from .models import Student, Teacher
from .serialize import studentSerializer, teacherSerializer


def get_tokens_for_user(user, role, user_id):
    """Helper function to generate JWT tokens"""
    refresh = RefreshToken()
    refresh["role"] = role
    refresh["user_id"] = user_id
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# ==============================
# 🔹 STUDENT AUTH
# ==============================

class StudentRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data.copy()
        data["password"] = make_password(data["password"])  # hash password
        serializer = studentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Student registered successfully"}, status=201)
        return Response(serializer.errors, status=400)


class StudentLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            student = Student.objects.get(username=username)
        except Student.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=401)

        if not check_password(password, student.password):
            return Response({"error": "Invalid username or password"}, status=401)

        tokens = get_tokens_for_user(student, "student", student.id)

        return Response({
            "msg": "Login successful",
            "user": studentSerializer(student).data,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "role": "student"
        })


# ==============================
# 🔹 TEACHER AUTH
# ==============================

class TeacherRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data.copy()
        data["password"] = make_password(data["password"])
        serializer = teacherSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Teacher registered successfully"}, status=201)
        return Response(serializer.errors, status=400)


class TeacherLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            teacher = Teacher.objects.get(email=email)
        except Teacher.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=401)

        if not check_password(password, teacher.password):
            return Response({"error": "Invalid email or password"}, status=401)

        tokens = get_tokens_for_user(teacher, "teacher", teacher.id)

        return Response({
            "msg": "Login successful",
            "user": teacherSerializer(teacher).data,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "role": "teacher"
        })


# ==============================
# 🔹 LOGOUT
# ==============================

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh"])
            token.blacklist()
            return Response({"msg": "Logged out successfully"}, status=200)
        except Exception:
            return Response({"error": "Invalid or expired token"}, status=400)
