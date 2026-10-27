"""Small, controlled error types. Endpoints turn these into clean HTTP errors."""


class AppError(Exception):
    pass


class NotFoundError(AppError):
    pass


class NoDataError(AppError):
    pass


class PersistenceError(AppError):
    pass
