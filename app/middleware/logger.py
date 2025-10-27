import logging
import logging.config
import time
from typing import Callable

import yaml
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

with open("config/logging.yaml", "r") as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)

logger = logging.getLogger("app_logger")


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_ip = request.client.host
        method = request.method
        url = str(request.url)

        logger.info(f"Incoming request: {method} {url} from {client_ip}")

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            raise
        finally:
            process_time = time.time() - start_time
            logger.info(
                f"Completed {method} {url} from {client_ip} in {process_time:.3f}s, status: {response.status_code}"
            )

        return response
