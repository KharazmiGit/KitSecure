from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
import requests
from django.conf import settings
import re

EXCLUDED_URLS = [
    r"^/auth/process/login/logic",
    # r"^/authentication/page",
    # Add other excluded URLs here
]


# LOGIN_URL = "/authentication/page"


def validate_token(token):
    introspect_url = f"{settings.KEYCLOAK_URL}/introspect"
    payload = {
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
        "token": token,
    }
    response = requests.post(introspect_url, data=payload)
    return response.status_code == 200 and response.json().get("active")


class KeycloakAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow OPTIONS requests (preflight requests for CORS)
        if request.method == "OPTIONS":
            response = JsonResponse({"message": "CORS preflight OK"}, status=200)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            return response

        # Exclude specific URLs
        for pattern in EXCLUDED_URLS:
            if re.match(pattern, request.path):
                return self.get_response(request)

        # Check for token in Authorization header
        auth_header = request.headers.get("Authorization")
        token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            # Check for token in cookies
            token = request.COOKIES.get("access_token")

        # Validate the token
        if not token or not validate_token(token):
            if request.headers.get("Accept") == "application/json":
                return JsonResponse({"error": "Unauthorized"}, status=401)
            return JsonResponse({"error": "Unauthorized. Please log in to access this resource."}, status=401)

        # If token is valid, proceed with the request
        return self.get_response(request)
