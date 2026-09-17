from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import LoginSerializer
from .models import LoginAttempt


@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):
    """Token-based login endpoint for API clients."""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"error": "Invalid input"}, status=400)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    user = User.objects.filter(email=email).first()
    if user is None:
        LoginAttempt.objects.create(
            email=email,
            success=False,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return Response({"error": "Invalid credentials"}, status=401)

    auth_user = authenticate(request, username=user.username, password=password)
    if auth_user is None:
        LoginAttempt.objects.create(
            email=email,
            success=False,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return Response({"error": "Invalid credentials"}, status=401)

    LoginAttempt.objects.create(
        user=user,
        email=email,
        success=True,
        ip_address=request.META.get("REMOTE_ADDR"),
    )
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=200)