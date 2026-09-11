"""Cliente oficial de la API de usuario de TempMailG.

La API evita depender del HTML protegido por Cloudflare/Turnstile. Requiere
una API key personal de TempMailG y la URL base que muestra su panel.
"""

import os
from typing import Any, Dict, List, Optional

import requests


class TempMailGAPIError(RuntimeError):
    pass


class TempMailGAPI:
    def __init__(self) -> None:
        self.base_url = os.getenv("TEMPMAILG_API_BASE_URL", "https://v1.tempmailg.com/api").rstrip("/")
        self.api_key = os.getenv("TEMPMAILG_API_KEY", "").strip()
        self.proxy = os.getenv("PROXY", "").strip()
        self.timeout = int(os.getenv("TEMPMAILG_API_TIMEOUT", "30"))

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        if not self.configured:
            raise TempMailGAPIError("TEMPMAILG_API_KEY no está configurada")
        headers = kwargs.pop("headers", {})
        headers.update({"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"})
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        response = requests.request(
            method,
            f"{self.base_url}/{path.lstrip('/')}",
            headers=headers,
            proxies=proxies,
            timeout=self.timeout,
            **kwargs,
        )
        try:
            data = response.json()
        except ValueError:
            data = {"status": False, "message": response.text[:500]}
        if not response.ok:
            message = data.get("message", f"HTTP {response.status_code}")
            raise TempMailGAPIError(f"TempMailG API {response.status_code}: {message}")
        if data.get("status") is False:
            raise TempMailGAPIError(data.get("message", "TempMailG API rechazó la solicitud"))
        return data

    def domains(self, kind: str = "free") -> List[Dict[str, Any]]:
        data = self._request("GET", f"domains?type={kind}")
        return data.get("data", {}).get("domains", [])

    def create_email(self) -> Dict[str, Any]:
        data = self._request("POST", "emails")
        return data.get("data", {})

    def delete_email(self, email: str) -> bool:
        self._request("DELETE", f"emails/{email}")
        return True

    def messages(self, email: str) -> List[Dict[str, Any]]:
        data = self._request("GET", "messages", params={"email": email})
        return data.get("messages", data.get("data", {}).get("messages", []))

    def message(self, message_id: str) -> Dict[str, Any]:
        data = self._request("GET", f"messages/{message_id}")
        return data.get("data", {})

    def attachment_url(self, message_id: str, filename: str) -> str:
        return f"{self.base_url}/messages/{message_id}/attachments/{filename}"
