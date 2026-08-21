from fastapi import status


class AppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BadRequestException(AppException):
    def __init__(self, message: str = "Yêu cầu không hợp lệ"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class NotFoundException(AppException):
    def __init__(self, message: str = "Tài nguyên không tồn tại"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Chưa xác thực hoặc token không hợp lệ"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Bạn không có quyền truy cập"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class InternalServerErrorException(AppException):
    def __init__(self, message: str = "Lỗi hệ thống nội bộ"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)