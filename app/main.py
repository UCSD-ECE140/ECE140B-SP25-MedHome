import mysql.connector
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uvicorn
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}

@app.post("/tempdata")
async def tempdata(request: Request):
    data = await request.json()
    temp = data.get("temp")
    return {"message": "Data received", "data": temp}

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return HTMLResponse(content=open("app/templates/index.html").read(), status_code=200)

@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard(request: Request):
    return HTMLResponse(content=open("app/templates/dashboard.html").read(), status_code=200)

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Show profile page"""
    with open("app/templates/profile.html") as html:
        return HTMLResponse(content=html.read())

@app.get("/export", response_class=HTMLResponse)
async def export_page(request: Request):
    """Show export page"""
    with open("app/templates/export.html") as html:
        return HTMLResponse(content=html.read())

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Show signup page"""
    with open("app/templates/signup.html") as html:
        return HTMLResponse(content=html.read())

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login if not logged in, or redirect to profile page"""
    with open("app/templates/login.html") as html:
        return HTMLResponse(content=html.read())

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="0.0.0.0", port=6543, reload=False)