from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "success": False,
                "status": 500,
                "error": "server_error",
                "message": "Internal server error",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    error_type = "error"
    message = "Something went wrong"
    details = None

    if isinstance(exc, ValidationError):
        error_type = "validation_error"
        message = "Invalid input"
        details = response.data

    elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        error_type = "authentication_error"
        message = "Authentication credentials were not provided."

    elif isinstance(exc, PermissionDenied):
        error_type = "permission_denied"
        message = "You do not have permission to perform this action."

    elif isinstance(exc, NotFound):
        error_type = "not_found"
        message = "Resource not found."

    return Response(
        {
            "success": False,
            "status": response.status_code,
            "error": error_type,
            "message": message,
            "details": details,
        },
        status=response.status_code,
    )
