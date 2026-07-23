"""
Sarvam AI Provider — Custom exceptions for clear, structured error handling.
"""


class SarvamError(Exception):
    """Base class for all Sarvam provider errors."""
    pass


class SarvamAuthError(SarvamError):
    """Raised when Sarvam API Key is missing or rejected."""
    pass


class SarvamAPIError(SarvamError):
    """Raised on non-2xx HTTP responses from Sarvam API."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Sarvam API Error [{status_code}]: {detail}")


class SarvamTimeoutError(SarvamError):
    """Raised when a Sarvam API request exceeds the configured timeout."""
    pass


class SarvamStreamError(SarvamError):
    """Raised when a streaming response from Sarvam is interrupted or malformed."""
    pass
