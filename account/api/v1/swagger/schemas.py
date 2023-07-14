from drf_spectacular.utils import extend_schema
from rest_framework import status

from .serializers import TokenPairSerializer, ErrorSerializer

obtain_token_schema = extend_schema(
    summary="Get JWT pair",
    responses={
        status.HTTP_200_OK: TokenPairSerializer,
        status.HTTP_400_BAD_REQUEST: ErrorSerializer,
        status.HTTP_401_UNAUTHORIZED: ErrorSerializer,
    }
)
