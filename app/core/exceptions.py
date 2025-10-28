from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class AppException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class EmailAlreadyRegisteredException(AppException):
    def __init__(
        self,
        detail: str = "Email already registered",
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(detail=detail, status_code=status_code)


class InvalidCredentialsException(AppException):
    def __init__(
        self,
        detail: str = "Invalid credentials",
        status_code=status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(detail=detail, status_code=status_code)


class SessionNotFoundException(AppException):
    def __init__(self, detail: str = "Session not found"):
        super().__init__(detail, status_code=status.HTTP_404_NOT_FOUND)


class SessionInvalidException(AppException):
    def __init__(self, detail: str = "Session is invalid or expired"):
        super().__init__(detail, status_code=status.HTTP_401_UNAUTHORIZED)


class InternalServerError(AppException):
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail, "path": str(request.url)},
    )
