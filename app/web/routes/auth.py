from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.get("/registration", response_class=HTMLResponse)
async def registration_page(request: Request):
    return templates.TemplateResponse(
        "registration.html", {"request": request, "error": None}
    )
