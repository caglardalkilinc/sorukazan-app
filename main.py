import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Soru Çöz Para Kazan API")

DB_FILE = "uygulama.db"

# Veritabanı Kurulumu ve TXT Dosyasından Soru Çekme
def veritabanini_hazirla():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE,
            bakiye REAL DEFAULT 0.0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sorular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soru_metni TEXT,
            secenek_a TEXT,
            secenek_b TEXT,
            secenek_c TEXT,
            secenek_d TEXT,
            dogru_cevap TEXT,
            odul_miktari REAL
        )
    ''')
    
    # Sadece veritabanı boşsa TXT'den soruları çek
    cursor.execute("SELECT COUNT(*) FROM sorular")
    if cursor.fetchone()[0] == 0:
        ornek_sorular = []
        if os.path.exists("sorular.txt"):
            with open("sorular.txt", "r", encoding="utf-8") as f:
                for satir in f:
                    satir = satir.strip()
                    if not satir or satir.startswith("#"):
                        continue
                    parcalar = satir.split("|")
                    if len(parcalar) == 7:
                        ornek_sorular.append((
                            parcalar[0].strip(),
                            parcalar[1].strip(),
                            parcalar[2].strip(),
                            parcalar[3].strip(),
                            parcalar[4].strip(),
                            parcalar[5].strip().upper(),
                            float(parcalar[6].strip())
                        ))
        
        # Eğer TXT dosyasında soru varsa veritabanına kaydet
        if ornek_sorular:
            cursor.executemany('''
                INSERT INTO sorular (soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, dogru_cevap, odul_miktari)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ornek_sorular)
        
        cursor.execute("INSERT OR IGNORE INTO kullanicilar (id, kullanici_adi, bakiye) VALUES (1, 'caglar', 0.0)")
        
    conn.commit()
    conn.close()

veritabanini_hazirla()

class CevapModel(BaseModel):
    kullanici_id: int
    soru_id: int
    secilen_secenek: str

@app.get("/", response_class=HTMLResponse)
def arayuzu_getir():
    html_yolu = os.path.join("templates", "index.html")
    if os.path.exists(html_yolu):
        with open(html_yolu, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>templates/index.html dosyası bulunamadı!</h3>"

@app.get("/api/kullanici/{kullanici_id}")
def kullanici_bilgisi(kullanici_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT kullanici_adi, bakiye FROM kullanicilar WHERE id = ?", (kullanici_id,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return {"kullanici_adi": user[0], "bakiye": round(user[1], 2)}

@app.get("/api/soru/{soru_id}")
def soru_getir(soru_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, odul_miktari FROM sorular WHERE id = ?", (soru_id,))
    soru = cursor.fetchone()
    conn.close()
    if not soru:
        return {"bitti": True, "mesaj": "Tüm soruları başarıyla tamamladınız!"}
    return {
        "bitti": False,
        "id": soru[0],
        "soru_metni": soru[1],
        "secenekler": {"A": soru[2], "B": soru[3], "C": soru[4], "D": soru[5]},
        "odul": soru[6]
    }

@app.post("/api/cevapla")
def cevap_kontrol_et(veri: CevapModel):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT dogru_cevap, odul_miktari FROM sorular WHERE id = ?", (veri.soru_id,))
    soru = cursor.fetchone()
    
    if not soru:
        conn.close()
        raise HTTPException(status_code=404, detail="Soru bulunamadı")
        
    dogru_cevap = soru[0]
    odul = soru[1]
    
    if veri.secilen_secenek == dogru_cevap:
        cursor.execute("UPDATE kullanicilar SET bakiye = bakiye + ? WHERE id = ?", (odul, veri.kullanici_id))
        conn.commit()
        conn.close()
        return {"durum": "dogru", "mesaj": f"Tebrikler! Doğru cevap. +{odul} TL kazanıldı.", "odul": odul}
    else:
        conn.close()
        return {"durum": "yanlis", "mesaj": "Yanlış cevap!"}