from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

# templates klasörünün yolunu projenin bulunduğu dizine göre ayarlar
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Eğer bu hata verirse, templates klasörü doğru yerde değil demektir
    return templates.TemplateResponse("index.html", {"request": request})
