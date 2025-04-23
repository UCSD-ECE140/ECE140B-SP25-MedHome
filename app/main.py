import mysql.connector
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime
import uvicorn
import os

from app.database import (
    setup_database,
    get_user_by_username,
    get_user_by_id,
    create_session,
    get_session,
    delete_session,
    create_user,
    create_device,
    get_device_by_device_mac,
    get_device_by_username,
    delete_device,
    add_sensor_data
)

INIT_USERS = {"alice": "pass123", "bob": "pass456"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for managing application startup and shutdown.
    Handles database setup and cleanup in a more structured way.
    """
    # Startup: Setup resources
    try:
        await setup_database(INIT_USERS)  # Make sure setup_database is async
        print("Database setup completed")
        yield
    finally:
        print("Shutdown completed")

app = FastAPI(lifespan=lifespan)

load_dotenv()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "port": os.getenv("MYSQL_PORT"),
    # "ssl_ca": os.getenv('MYSQL_SSL_CA'),
    # "ssl_verify_identity": True
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_error_html(username: str) -> str:
    error_html = open("app/templates/error.html").read()
    return error_html.replace("{username}", username)

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

@app.get("/profile/user/{username}", response_class=HTMLResponse)
async def user_page(username: str, request: Request):
    """Show user profile if authenticated, error if not"""
    # TODO: 11. Get sessionId from cookies
    session_id = request.cookies.get("sessionId")

    # TODO: 12. Check if sessionId exists and is valid
    #   - if not, redirect to /login
    current_session = await get_session(session_id)
    if current_session is None:
        return RedirectResponse(url="/login", status_code=302)
    user_with_id = await get_user_by_id(current_session["user_id"])
    
    # TODO: 13. Check if session username matches URL username
    #   - if not, return error page using get_error_html with 403 status
    
    if user_with_id["username"] != username:
        return HTMLResponse(content=get_error_html(username), status_code=403)

    # TODO: 14. If all valid, show profile page
    else: 
        with open("app/templates/profile.html") as html:
            return HTMLResponse(content=html.read())

@app.post("/profile/user/{username}", response_class=HTMLResponse)
async def login(username: str, request: Request):
    """Validate credentials and create a new session if valid"""
    form_data = await request.form()
    device_mac = form_data.get("device-name")

    device_id = await get_device_by_device_mac(device_mac)
    await create_device(username, device_mac)
    
    return RedirectResponse(url=f"/profile/user/{username}", status_code=302)

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
    id = request.cookies.get("sessionId")
    if id:
        print(id)
        id = await get_session(id)
        if id:
            username = await get_user_by_id(id["user_id"])
            return RedirectResponse(url=f"/profile/user/{username['username']}", status_code=302)
        else:
            with open("app/templates/login.html") as html:
                return HTMLResponse(content=html.read()) 
    else:
        with open("app/templates/login.html") as html:
            return HTMLResponse(content=html.read())

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Validate credentials and create a new session if valid"""
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    # TODO: 5. Check if username exists and password matches
    user = await get_user_by_username(username)
    if user is not None:
        if user["password"] == password:
            pass
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        raise HTTPException(status_code=404, detail="User not found")

    # TODO: 6. Create a new session
    session_id = str(uuid.uuid4())
    new_session = await create_session(user["id"], session_id)

    # TODO: 7. Create response with:
    #   - redirect to /user/{username}
    #   - set cookie with session ID
    #   - return the response
    response = RedirectResponse(url=f"/profile/user/{username}", status_code=302)
    response.set_cookie(key="sessionId", value=session_id)
    return response

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="0.0.0.0", port=6543, reload=False)