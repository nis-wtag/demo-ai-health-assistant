from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from core.database import DbSession

class RefreshTokenMiddleWare(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next, db: DbSession):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
