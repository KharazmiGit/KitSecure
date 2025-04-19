from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
from django.views.decorators.csrf import csrf_exempt
import jwt
from rest_framework.authentication import get_authorization_header

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
        access_token = token_data.get("access_token")

        # Decode token to extract Keycloak user ID
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        keycloak_user_id = decoded.get("sub")

        if not keycloak_user_id:
            return Response(
                {"error": "Keycloak ID (sub) not found in token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create or get user based on keycloak_id
        user, created = User.objects.get_or_create(
            keycloak_id=keycloak_user_id,
            defaults={"username": username}
        )

        if created:
            user.set_unusable_password()
            user.save()

        login(request, user)

        return JsonResponse({
            "access_token": access_token,
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
            "token_type": token_data.get("token_type"),
            "user_created": created,
            "keycloak_id": keycloak_user_id,
            "userId": user.id,
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


def get_keycloak_id_from_request(request):
    auth_header = get_authorization_header(request).split()
    if not auth_header or auth_header[0].lower() != b'bearer':
        return None

    token = auth_header[1]
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        return decoded_token.get("sub")  # 'sub' is the user's unique Keycloak ID
    except Exception as e:
        print("Token decoding error:", e)
        return None
