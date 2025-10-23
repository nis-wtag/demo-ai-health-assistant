import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("app.log")
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host
        method = request.method
        url = str(request.url)

        logger.info(f"Incoming request: {method} {url} from {client_ip}")

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            raise e

        process_time = time.time() - start_time
        logger.info(
            f"Completed {method} {url} from {client_ip} in {process_time:.3f}s, status: {response.status_code}"
        )

        return response
