# region new version

from django.shortcuts import render
from . import serializers
from .models import UserAction
from rest_framework import generics
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from io import BytesIO
import json
from auth_process.views import get_keycloak_id_from_request
import logging

logger = logging.getLogger(__name__)


# --- API to Create Tracked Actions ---
class CreateTrackedUserActions(generics.CreateAPIView):
    queryset = UserAction.objects.all()
    serializer_class = serializers.UserActionSerializers

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

        # --- Load from DB ---


def get_user_actions_from_db(keycloak_id):
    try:
        actions = UserAction.objects.filter(user__keycloak_id=keycloak_id)
        print(keycloak_id)
        actions_data = []
        for action in actions:
            if isinstance(action.json_data, str):
                actions_data.append(json.loads(action.json_data))  # If stored as string
            else:
                actions_data.append(action.json_data)  # Already a list/dict
        return actions_data
    except Exception as e:
        logger.error(f"Failed to fetch user actions for {keycloak_id}: {e}")
        return []


# --- Convert JSON to Python Code ---
def convert_json_to_python_code(json_data):
    python_code = []
    for action in json_data:
        if action['type'] == 'visit':
            python_code.append(f"browser.get('{action['url']}')")
        elif action['type'] == 'input':
            python_code.append(f"browser.find_element_by_id('{action['target']}').send_keys('{action['value']}')")
        elif action['type'] == 'click':
            python_code.append(f"browser.find_element_by_id('{action['target']}').click()")
    return '\n'.join(python_code)


# --- Download as Excel File ---
def download_python_code_excel(request):
    keycloak_id = get_keycloak_id_from_request(request)
    if not keycloak_id:
        return HttpResponse("Unauthorized", status=401)
    users_data = get_user_actions_from_db(keycloak_id=keycloak_id)

    # Flatten all the actions if multiple entries contain lists
    flattened_data = []
    for entry in users_data:
        if isinstance(entry, list):
            flattened_data.extend(entry)
        else:
            flattened_data.append(entry)

    # Generate code
    python_code = convert_json_to_python_code(flattened_data)

    # Write to Excel in-memory
    wb = Workbook()
    ws = wb.active
    ws.title = "Generated Code"
    for idx, line in enumerate(python_code.split("\n"), start=1):
        ws.cell(row=idx, column=1).value = line

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=python_code.xlsx'
    return response


# endregion


# region old version

# from django.shortcuts import render
# from . import serializers
# from .models import UserAction
# from rest_framework import generics
# from django.http import HttpResponse
# from openpyxl import Workbook
# from openpyxl.utils import get_column_letter
# from io import BytesIO
# import json
#
#
# # --- API to Create Tracked Actions ---
# class CreateTrackedUserActions(generics.CreateAPIView):
#     queryset = UserAction.objects.all()
#     serializer_class = serializers.UserActionSerializers
#
#     def perform_create(self, serializer):
#         if self.request.user.is_authenticated:
#             serializer.save(user=self.request.user)
#         else:
#             serializer.save()
#
#         # --- Load from DB ---
#
#
# def get_user_actions_from_db():
#     actions = UserAction.objects.all()
#     actions_data = []
#     for action in actions:
#         if isinstance(action.json_data, str):
#             actions_data.append(json.loads(action.json_data))  # If stored as string
#         else:
#             actions_data.append(action.json_data)  # Already a list/dict
#     return actions_data
#
#
# # --- Convert JSON to Python Code ---
# def convert_json_to_python_code(json_data):
#     python_code = []
#     for action in json_data:
#         if action['type'] == 'visit':
#             python_code.append(f"browser.get('{action['url']}')")
#         elif action['type'] == 'input':
#             python_code.append(f"browser.find_element_by_id('{action['target']}').send_keys('{action['value']}')")
#         elif action['type'] == 'click':
#             python_code.append(f"browser.find_element_by_id('{action['target']}').click()")
#     return '\n'.join(python_code)
#
#
# # --- Download as Excel File ---
# def download_python_code_excel(request):
#     all_data = get_user_actions_from_db()
#
#     # Flatten all the actions if multiple entries contain lists
#     flattened_data = []
#     for entry in all_data:
#         if isinstance(entry, list):
#             flattened_data.extend(entry)
#         else:
#             flattened_data.append(entry)
#
#     # Generate code
#     python_code = convert_json_to_python_code(flattened_data)
#
#     # Write to Excel in-memory
#     wb = Workbook()
#     ws = wb.active
#     ws.title = "Generated Code"
#     for idx, line in enumerate(python_code.split("\n"), start=1):
#         ws.cell(row=idx, column=1).value = line
#
#     buffer = BytesIO()
#     wb.save(buffer)
#     buffer.seek(0)
#
#     response = HttpResponse(
#         buffer,
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
#     response['Content-Disposition'] = 'attachment; filename=python_code.xlsx'
#     return response

# endregion
