class EmployeeImportError(Exception):
    pass


class EmployeeImportValidationError(EmployeeImportError):
    def __init__(self, message: str, *, missing_columns: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.missing_columns = missing_columns or []
