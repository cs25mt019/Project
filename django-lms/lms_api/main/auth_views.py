# main/auth_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .models import Student, Teacher
from .serialize import studentSerializer, teacherSerializer
from datetime import timedelta
from django.contrib.auth.hashers import make_password


def get_tokens_for_user(user, role, user_id):
    """
    Create refresh and access tokens for the given user.
    Uses RefreshToken.for_user(user) so the token is properly linked to 'user'.
    Adds custom claims: role, user_id, name.
    """
    # Create refresh token associated with the user
    refresh = RefreshToken.for_user(user)

    # Add custom claims to refresh
    refresh["role"] = role
    refresh["user_id"] = user_id
    refresh["name"] = getattr(user, "full_name", "")

    # Derive access token from refresh and add same claims
    access = refresh.access_token
    access["role"] = role
    access["user_id"] = user_id
    access["name"] = getattr(user, "full_name", "")

    return {
        "refresh": str(refresh),
        "access": str(access),
    }

# ======================================
# STUDENT REGISTER
# ======================================
from rest_framework import permissions as _perms

class StudentRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Body:
        {
          "full_name": "...",
          "email": "...",
          "username": "...",
          "password": "...",
          "interested_categories": "..."
        }
        Note: Student model.save() hashes password.
        """
        data = request.data.copy()

        if not data.get("password"):
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get("username") or not data.get("email"):
            return Response({"error": "username and email are required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = studentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Student registered successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ======================================
# STUDENT LOGIN
# ======================================
class StudentLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "username and password required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(username=username)
        except Student.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, student.password):
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_user(student, "student", student.id)

        return Response({
            "msg": "Login successful",
            "user": studentSerializer(student).data,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "role": "student"
        }, status=status.HTTP_200_OK)


# ======================================
# TEACHER REGISTER
# ======================================
class TeacherRegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        data = request.data.copy()

        if not data.get("password"):
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = teacherSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Teacher registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ======================================
# TEACHER LOGIN
# ======================================
class TeacherLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            teacher = Teacher.objects.get(email=email)
        except Teacher.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, teacher.password):
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_user(teacher, "teacher", teacher.id)

        return Response({
            "msg": "Login successful",
            "user": {
                "id": teacher.id,
                "full_name": teacher.full_name,
                "email": teacher.email
            },
            **tokens,
            "role": "teacher"
        }, status=status.HTTP_200_OK)


# ======================================
# LOGOUT
# ======================================
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            #token = RefreshToken(refresh_token)
            #token.blacklist()
            return Response({"msg": "Logout successful"}, status=200)

            #return Response({"msg": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

from django.core.mail import send_mail
from django.utils import timezone
import random
from .models import PasswordResetOTP, Student, Teacher

class RequestResetOTP(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        # Determine user type
        user = None
        user_type = None

        try:
            user = Student.objects.get(email=email)
            user_type = "student"
        except Student.DoesNotExist:
            try:
                user = Teacher.objects.get(email=email)
                user_type = "teacher"
            except Teacher.DoesNotExist:
                pass  # Do NOT reveal user existence

        # Always respond with a generic message
        if not user:
            return Response({"message": "If this email exists, an OTP has been sent."}, status=200)

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Create DB record
        PasswordResetOTP.objects.create(
            email=email,
            otp=otp,
            user_type=user_type,
            user_id=user.id,
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        # Send email
        send_mail(
            subject="Your Password Reset OTP",
            message=f"Your OTP is {otp}. It will expire in 5 minutes.",
            from_email=None,
            recipient_list=[email],
        )

        return Response({"message": "If this email exists, an OTP has been sent."}, status=200)


class VerifyResetOTP(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=400)

        record = PasswordResetOTP.objects.filter(
            email=email, otp=otp, used=False
        ).order_by("-created_at").first()

        if not record:
            return Response({"error": "Invalid OTP"}, status=400)

        if record.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        record.verified = True
        record.save()

        return Response({"message": "OTP verified successfully"}, status=200)

class ResetPassword(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not email or not otp or not new_password:
            return Response({"error": "email, otp, new_password required"}, status=400)

        record = PasswordResetOTP.objects.filter(
            email=email, otp=otp, verified=True, used=False
        ).order_by("-created_at").first()

        if not record:
            return Response({"error": "Invalid or unverified OTP"}, status=400)

        if record.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        # Update password
        if record.user_type == "student":
            user = Student.objects.get(id=record.user_id)
        else:
            user = Teacher.objects.get(id=record.user_id)

        user.password = make_password(new_password)
        user.save()

        record.used = True
        record.save()

        return Response({"message": "Password reset successful"}, status=200)
