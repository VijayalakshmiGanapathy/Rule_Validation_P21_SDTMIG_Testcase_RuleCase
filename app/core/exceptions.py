class FileMissingError(Exception):
    """Raised when a required file is missing."""


class SheetMissingError(Exception):
    """Raised when a required sheet is missing."""


class ValidationError(Exception):
    """Raised when validation fails."""