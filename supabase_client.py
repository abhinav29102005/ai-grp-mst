"""
Supabase client helper -- lightweight REST wrapper using httpx.
Avoids the heavy 'supabase' SDK and its native-compilation dependencies.
"""

from __future__ import annotations
import httpx
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY

REST_BASE = f"{SUPABASE_URL}/rest/v1"


class _QueryResponse:
    """Minimal response wrapper matching the pattern used by the rest of the app."""
    def __init__(self, data: list):
        self.data = data


class _TableQuery:
    """Fluent builder for PostgREST queries."""

    def __init__(self, table: str, headers: dict, http: httpx.Client):
        self._url = f"{REST_BASE}/{table}"
        self._headers = {**headers}
        self._params: dict[str, str] = {}
        self._method = "GET"
        self._body: list | dict | None = None
        self._http = http

    # --- SELECT / filters ---------------------------------------------------
    def select(self, columns: str = "*"):
        self._params["select"] = columns
        return self

    def limit(self, n: int):
        self._params["limit"] = str(n)
        return self

    def order(self, column: str, desc: bool = False):
        direction = "desc" if desc else "asc"
        self._params["order"] = f"{column}.{direction}"
        return self

    def eq(self, column: str, value):
        self._params[column] = f"eq.{value}"
        return self

    def gte(self, column: str, value):
        self._params[column] = f"gte.{value}"
        return self

    # --- INSERT / DELETE ----------------------------------------------------
    def insert(self, rows: list[dict]):
        self._method = "POST"
        self._body = rows
        self._headers["Prefer"] = "return=minimal"
        return self

    def delete(self):
        self._method = "DELETE"
        self._headers["Prefer"] = "return=minimal"
        return self

    # --- EXECUTE ------------------------------------------------------------
    def execute(self) -> _QueryResponse:
        client = self._http
        if self._method == "GET":
            resp = client.get(self._url, headers=self._headers, params=self._params)
        elif self._method == "POST":
            resp = client.post(
                self._url,
                headers={**self._headers, "Content-Type": "application/json"},
                params=self._params,
                json=self._body,
            )
        elif self._method == "DELETE":
            resp = client.delete(self._url, headers=self._headers, params=self._params)
        else:
            raise ValueError(f"Unsupported method {self._method}")

        if resp.status_code >= 400:
            raise RuntimeError(f"Supabase error {resp.status_code}: {resp.text[:300]}")

        try:
            data = resp.json()
        except Exception:
            data = []

        return _QueryResponse(data if isinstance(data, list) else [])


class SupabaseClient:
    """Minimal Supabase REST client."""

    def __init__(self, url: str, key: str):
        self._url = url
        self._headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
        }
        self._http = httpx.Client(timeout=120)

    def table(self, name: str) -> _TableQuery:
        return _TableQuery(name, self._headers, self._http)


# ---------- Convenience singletons -----------------------------------------

_service_client: SupabaseClient | None = None
_anon_client: SupabaseClient | None = None


def get_service_client() -> SupabaseClient:
    """Get a Supabase client with service role privileges (full access)."""
    global _service_client
    if _service_client is None:
        _service_client = SupabaseClient(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _service_client


def get_anon_client() -> SupabaseClient:
    """Get a Supabase client with anon privileges (read-only via RLS)."""
    global _anon_client
    if _anon_client is None:
        _anon_client = SupabaseClient(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _anon_client