"""
Sarvam AI Provider — Async HTTP client with retry and timeout support.
"""
import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from friday.providers.sarvam.sarvam_config import SarvamConfig
from friday.providers.sarvam.sarvam_exceptions import (
    SarvamAPIError,
    SarvamAuthError,
    SarvamTimeoutError,
)

logger = logging.getLogger(__name__)


class SarvamClient:
    """
    Async HTTP client for Sarvam AI REST API.

    Handles authentication, request retries, timeout management, and
    structured error surfacing.
    """

    def __init__(self, config: SarvamConfig, max_retries: int = 3):
        self.config = config
        self.max_retries = max_retries
        self._base_url = config.BASE_URL.rstrip("/")

        if not config.api_key:
            raise SarvamAuthError(
                "SARVAM_API_KEY is missing. Provide it via .env or environment variables."
            )

    def _headers(self) -> Dict[str, str]:
        return {
            "api-subscription-key": self.config.api_key,
            "Content-Type": "application/json",
        }

    def _headers_multipart(self) -> Dict[str, str]:
        """Headers for multipart/form-data requests (STT file upload)."""
        return {
            "api-subscription-key": self.config.api_key,
        }

    async def post_json(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Sends a POST request with JSON body to the Sarvam API.
        Retries up to max_retries times on transient failures.
        """
        url = f"{self._base_url}{endpoint}"
        timeout = timeout or self.config.timeout

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url, headers=self._headers(), json=payload)

                if response.status_code == 401:
                    raise SarvamAuthError("Sarvam API rejected the API key (401 Unauthorized).")

                if response.status_code >= 400:
                    raise SarvamAPIError(response.status_code, response.text)

                return response.json()

            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                logger.warning(
                    f"[SarvamClient] Attempt {attempt}/{self.max_retries} failed: {exc}"
                )
                if attempt == self.max_retries:
                    raise SarvamTimeoutError(
                        f"Sarvam API timed out after {self.max_retries} attempts."
                    ) from exc
                await asyncio.sleep(0.5 * attempt)  # exponential-ish back-off

    async def post_multipart(
        self,
        endpoint: str,
        files: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Sends a POST request with multipart/form-data (used by STT to upload audio).
        """
        url = f"{self._base_url}{endpoint}"
        timeout = timeout or self.config.timeout

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        url,
                        headers=self._headers_multipart(),
                        files=files,
                        data=data or {},
                    )

                if response.status_code == 401:
                    raise SarvamAuthError("Sarvam API rejected the API key (401 Unauthorized).")

                if response.status_code >= 400:
                    raise SarvamAPIError(response.status_code, response.text)

                return response.json()

            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                logger.warning(
                    f"[SarvamClient] Multipart attempt {attempt}/{self.max_retries} failed: {exc}"
                )
                if attempt == self.max_retries:
                    raise SarvamTimeoutError(
                        f"Sarvam STT upload timed out after {self.max_retries} attempts."
                    ) from exc
                await asyncio.sleep(0.5 * attempt)
