"""Custom exceptions for nfe2pdf domain."""
from __future__ import annotations


class NFe2PDFError(Exception):
    """Base exception for nfe2pdf errors."""
    pass


class InvalidXmlError(NFe2PDFError):
    """Raised when XML is malformed or cannot be parsed."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(message)


class NotNFeError(NFe2PDFError):
    """Raised when XML is valid but not an NF-e (wrong namespace/root)."""

    def __init__(self, message: str, root_tag: str | None = None, namespace: str | None = None):
        self.root_tag = root_tag
        self.namespace = namespace
        super().__init__(message)


class InvalidNFeVersionError(NFe2PDFError):
    """Raised when NF-e version is not supported."""

    def __init__(self, message: str, found_version: str | None = None):
        self.found_version = found_version
        super().__init__(message)


class MissingRequiredFieldError(NFe2PDFError):
    """Raised when a required field is missing from the XML."""

    def __init__(self, message: str, field_path: str | None = None):
        self.field_path = field_path
        super().__init__(message)


class PDFGenerationError(NFe2PDFError):
    """Raised when PDF generation fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(message)


class ConfigurationError(NFe2PDFError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str | None = None):
        self.config_key = config_key
        super().__init__(message)


class FileAssociationError(NFe2PDFError):
    """Raised when Windows file association fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(message)


class ValidationError(NFe2PDFError):
    """Raised when data validation fails (Pydantic validation errors)."""

    def __init__(self, message: str, errors: list | None = None):
        self.errors = errors
        super().__init__(message)