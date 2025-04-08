from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login_logic_view(request):
    data = request.data

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 1: Authenticate against Keycloak
    payload = {
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    try:
        keycloak_response = requests.post(settings.KEYCLOAK_URL, data=payload)

        if keycloak_response.status_code != 200:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token_data = keycloak_response.json()

        # Step 2: Ensure user exists in local DB
        user, created = User.objects.get_or_create(username=username)

        if created:
            # You can also pull more user info from Keycloak here if needed
            user.set_unusable_password()  # Password is managed by Keycloak
            user.save()

        # Step 3: Log the user into the local Django session
        login(request, user)

        return JsonResponse({
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
            "token_type": token_data.get("token_type"),
            "user_created": created,
            "message": "User logged in successfully"
        }, status=status.HTTP_200_OK)

    except requests.RequestException as e:
        return Response(
            {"error": f"Keycloak request failed: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY
        )

    except Exception as e:
        return Response(
            {"error": f"Internal server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
