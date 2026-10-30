from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def index():
    return "<!doctype html><meta charset='utf-8'><title>앱</title><h1>뼈대가 돌아갑니다</h1>"
