"""Error response factory for CodeRef MCP Service."""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ErrorResponse:
    """Standard error response structure."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'error_code': self.error_code,
            'message': self.message,
        }
        if self.details:
            result['details'] = self.details
        return result


class ErrorFactory:
    """Factory for creating standardized error responses."""

    @staticmethod
    def validation_error(message: str, details: Optional[Dict] = None) -> ErrorResponse:
        """Create a validation error response."""
        return ErrorResponse(
            error_code='VALIDATION_ERROR',
            message=message,
            details=details
        )

    @staticmethod
    def reference_not_found(reference: str, details: Optional[Dict] = None) -> ErrorResponse:
        """Create a reference not found error."""
        return ErrorResponse(
            error_code='REFERENCE_NOT_FOUND',
            message=f'Reference not found: {reference}',
            details=details or {'reference': reference}
        )

    @staticmethod
    def service_error(message: str, details: Optional[Dict] = None) -> ErrorResponse:
        """Create a service error response."""
        return ErrorResponse(
            error_code='SERVICE_ERROR',
            message=message,
            details=details
        )

    @staticmethod
    def invalid_format(message: str, details: Optional[Dict] = None) -> ErrorResponse:
        """Create an invalid format error."""
        return ErrorResponse(
            error_code='INVALID_FORMAT',
            message=message,
            details=details
        )

    @staticmethod
    def timeout_error(operation: str, timeout_ms: int) -> ErrorResponse:
        """Create a timeout error."""
        return ErrorResponse(
            error_code='TIMEOUT_ERROR',
            message=f'Operation "{operation}" exceeded timeout ({timeout_ms}ms)',
            details={'operation': operation, 'timeout_ms': timeout_ms}
        )

    @staticmethod
    def unavailable_service(service_name: str) -> ErrorResponse:
        """Create a service unavailable error."""
        return ErrorResponse(
            error_code='SERVICE_UNAVAILABLE',
            message=f'Service unavailable: {service_name}',
            details={'service': service_name}
        )

    @staticmethod
    def generic_error(message: str, details: Optional[Dict] = None) -> ErrorResponse:
        """Create a generic error response."""
        return ErrorResponse(
            error_code='GENERIC_ERROR',
            message=message,
            details=details
        )
