from api.v1.api import api_router as api_v1_router
from core.config import settings
from core.exceptions import AppException, app_exception_handler
from core.limiter import limiter, rate_limit_exceeded_handler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from middleware.auto_refresh import AutoRefreshMiddleware
from middleware.logger import LoggingMiddleware, logger
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from web.routes import router as web_router

app = FastAPI(title="AI Health Assistant", version="0.1.0")

app.add_middleware(LoggingMiddleware)
app.add_exception_handler(AppException, app_exception_handler)

app.add_middleware(AutoRefreshMiddleware)

if settings.APP_ENV != "test":
    logger.info("Rate limiting middleware enabled.")
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
else:
    logger.info("Rate limiting middleware DISABLED for testing.")
    limiter.enabled = False


app.include_router(api_v1_router)
app.include_router(web_router, tags=["Web"])

app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.mount("/image", StaticFiles(directory="data/doctors/image"), name="image")


@app.get("/")
def root():
    return {"message": "Welcome to the AI Health Assistant (AHA)"}
