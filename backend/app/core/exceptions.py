"""Application errors mapped to HTTP responses in API layer."""


class AppError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValidationError(AppError):
    pass


class NotFoundError(AppError):
    pass
