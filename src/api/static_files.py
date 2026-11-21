from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope

from src.config import API_PREFIX


class AppStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        request_path = scope.get("path", "")
        if request_path == API_PREFIX or request_path.startswith(f"{API_PREFIX}/"):
            raise HTTPException(status_code=404)
        return await super().get_response(path, scope)
