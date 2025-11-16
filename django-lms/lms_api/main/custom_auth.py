# main/custom_auth.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .models import Student, Teacher

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Use role/user_id claims from token to fetch Student/Teacher.
        validated_token is the validated token dict-like object.
        """
        # use .get to avoid KeyError; raise InvalidToken if user_id missing
        user_id = validated_token.get("user_id")
        role = validated_token.get("role")

        if user_id is None:
            raise InvalidToken("Token did not contain 'user_id' claim")

        # ensure integer id when string provided
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            raise InvalidToken("Invalid 'user_id' in token")

        if role == "student":
            try:
                return Student.objects.get(id=user_id)
            except Student.DoesNotExist:
                raise AuthenticationFailed("User not found", code="user_not_found")
        elif role == "teacher":
            try:
                return Teacher.objects.get(id=user_id)
            except Teacher.DoesNotExist:
                raise AuthenticationFailed("User not found", code="user_not_found")
        else:
            raise AuthenticationFailed("Invalid role in token")
