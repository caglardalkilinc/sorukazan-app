from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Veritabanı kurulumu
conn = sqlite3.connect("tengri_medya.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, phone TEXT, balance REAL)")
conn.commit()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/register")
async def register(name: str = Form(...), phone: str = Form(...)):
    conn.execute("INSERT INTO users VALUES (?, ?, 0.0)", (name, phone))
    conn.commit()
    return {"message": "Kayıt Başarılı", "name": name}
