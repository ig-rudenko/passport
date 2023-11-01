from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .validators import RequestCodeValidator


class CodePermission(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return RequestCodeValidator(request).validate()
