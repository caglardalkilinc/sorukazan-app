from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_sorular():
    sorular = []
    if os.path.exists("sorular.txt"):
        with open("sorular.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 7:
                    sorular.append({
                        "soru": parts[0], "a": parts[1], "b": parts[2], 
                        "c": parts[3], "d": parts[4], "dogru": parts[5], "odul": parts[6]
                    })
    return sorular

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "sorular": get_sorular()})
