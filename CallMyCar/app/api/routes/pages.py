from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["pages"])


@router.get("/", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/setup", include_in_schema=False)
def setup_page(request: Request):
    return templates.TemplateResponse("setup.html", {"request": request})


@router.get("/v/{qr_code_id}", include_in_schema=False)
def scan_page(request: Request, qr_code_id: str):
    return templates.TemplateResponse(
        "scan.html", {"request": request, "qr_code_id": qr_code_id}
    )
