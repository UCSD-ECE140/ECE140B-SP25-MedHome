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
import bcrypt
from app.data_analysis import dataAnalyzer

def hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except ValueError:
        print(f"[!] Invalid password hash detected: {hashed_password}")
        return False

from app.database import (
    setup_database,
    get_user_by_username,
    get_user_by_id,
    get_user_by_serial_num,
    create_session,
    get_session,
    delete_session,
    create_user,
    add_data_to_user,
    create_device,
    get_device_by_serial_num,
    get_device_by_username,
    delete_device, 
    get_data_from_user
)

from app.pdf import generate_health_report


async def verify_user(username: str, request: Request) -> bool:
    """
    Verify if the provided username matches the current session of the client.
    """
    # Get sessionId from cookies
    session_id = request.cookies.get("sessionId")

    # Check if sessionId exists and is valid
    #   - if not, redirect to /login
    current_session = await get_session(session_id)
    if current_session is None:
        return False
    user_with_id = await get_user_by_id(current_session["user_id"])
    
    # Check if session username matches URL username
    #   - if not, return false else return true
    return user_with_id["username"] == username


INIT_USERS = {
    "alice": ("Alice", "Smith", "alice@example.com", "alice", hash_password("pass123"), "MH-830B35DF"),
    "bob": ("Bob", "Johnson", "bob@example.com", "bob", hash_password("pass456"), "MH-EAF7EF67")
}

def generate_serial_number() -> str:
    """Generate a unique serial number."""
    return f"MH-{uuid.uuid4().hex[:8].upper()}"

INIT_USER_DEVICES = {
    ("alice", "MH-830B35DF"),
    ("bob", "MH-EAF7EF67")
}

INIT_DEVICES = [generate_serial_number() for i in range(2)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for managing application startup and shutdown.
    Handles database setup and cleanup in a more structured way.
    """
    # Startup: Setup resources
    try:
        await setup_database(INIT_USERS, INIT_USER_DEVICES, INIT_DEVICES)  # Make sure setup_database is async
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

@app.post("/data")
async def dataPost(request: Request):
    data = await request.json()
    if data is None:
        return {"message": "No data received"}
    temp = data.get("heart_rate")
    return {"message": "Data received", "data": temp}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return HTMLResponse(content=open("app/templates/index.html").read(), status_code=200)

@app.post("/avgHRavgSpO2weightbpSbpD")
async def avgHRavgSpO2weightbpSbpD(request: Request):
    data = await request.json()
    # Validate required fields
    required_fields = ["serial_number", "avgHR", "avgSpO2", "weight", "bpS", "bpD"]
    if not all(field in data for field in required_fields):
        return {"error": "Missing one or more required fields."}
    # You can add database storage or processing here if needed

    add_data_to_user(get_user_by_serial_num(data["serial_number"]), data)
    
    return {
            "message": "Data received successfully",
            "serial_number": data["serial_number"],
            "avgHR": data["avgHR"],
            "avgSpO2": data["avgSpO2"],
            "weight": data["weight"],
            "bpS": data["bpS"],
            "bpD": data["bpD"]
        }
    
@app.get("/dashboard/user/{username}/data") 
async def get_dashboard_data(username: str, request: Request): 
    if(await verify_user(username, request)): 
        theData = await get_data_from_user(username); 
        # print(theData); 
        # return HTMLResponse(content = theData, status_code = 200); 
        # Data order: avgHR, avgSpO2, weight, bpS, bpD

        avgHR = []; avgSpO2 = []; weight = []; bpS = []; bpD = []; 

        for i in range(7):
            aDataList = theData[i]; 
            avgHR.append(aDataList[0]); 
            avgSpO2.append(aDataList[1]); 
            weight.append(aDataList[2]); 
            bpS.append(aDataList[3]); 
            bpD.append(aDataList[4]); 

        theResponse = ""; 
        theAnalyst = dataAnalyzer(); 

        theResponse += theAnalyst.analyze_avgHR(avgHR); 
        theResponse += theAnalyst.analyze_avgSpO2(avgSpO2); 
        theResponse += theAnalyst.analyze_weight(weight); 
        theResponse += theAnalyst.analyze_blood_pressure(bpS, bpD); 
    
        return HTMLResponse(content = "{\"theResponse\": \"" + theResponse + "\"}", status_code = 200); 


    else:
        return HTMLResponse(content=get_error_html(username), status_code=403)

@app.get("/dashboard/user/{username}", response_class=HTMLResponse)
async def read_dashboard(username: str, request: Request):
    if(await verify_user(username, request)):
        with open("app/templates/dashboard.html") as html:
            return HTMLResponse(content=html.read())
    else:
        return HTMLResponse(content=get_error_html(username), status_code=403)

@app.post("/dashboard/user/{username}", response_class=HTMLResponse)
async def profile(username: str, request: Request):
    return RedirectResponse(url=f"/dashboard/user/{username}", status_code=302)

@app.get("/profile/user/{username}", response_class=HTMLResponse)
async def user_page(username: str, request: Request):
    """Show user profile if authenticated, error if not"""
    if(await verify_user(username, request)):
        with open("app/templates/profile.html") as html:
            return HTMLResponse(content=html.read())
    else:
        return HTMLResponse(content=get_error_html(username), status_code=403)

@app.post("/profile/user/{username}", response_class=HTMLResponse)
async def profile(username: str, request: Request):
    return RedirectResponse(url=f"/profile/user/{username}", status_code=302)

@app.get("/export/user/{username}", response_class=HTMLResponse)
async def export_page(username: str, request: Request):
    """Show export page"""
    if(await verify_user(username, request)):
        with open("app/templates/export.html") as html:
            return HTMLResponse(content=html.read())
    else:
        return HTMLResponse(content=get_error_html(username), status_code=403)

@app.post("/export/user/{username}", response_class=HTMLResponse)
async def export(username: str, request: Request):
    return RedirectResponse(url=f"/export/user/{username}", status_code=302)

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Show signup page"""
    with open("app/templates/signup.html") as html:
        return HTMLResponse(content=html.read())

@app.post("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    try:
        """Create a new user and redirect to /login"""
        form_data = await request.form()
        username = form_data.get("user")
        first_name = form_data.get("fname")
        last_name = form_data.get("lname")
        email = form_data.get("email")
        password = hash_password(form_data.get("password"))

        # Check if username already exists
        existing_user = await get_user_by_username(username)
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Create new user
        await create_user(username, first_name, last_name, email, password)

        # Redirect to /login
        return RedirectResponse(url="/login", status_code=302)
    
    except Exception as e:
        print(f"[!] Signup failed: {e}")
        return HTMLResponse(content="Signup failed: " + str(e), status_code=500)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login page"""
    # Get sessionId from cookies
    session_id = request.cookies.get("sessionId")
    
    # Check if sessionId exists and is valid
    #   - if not, redirect to /login
    current_session = await get_session(session_id)
    if current_session is not None:
        user_with_id = await get_user_by_id(current_session["user_id"])
        username = user_with_id["username"]
        # Redirect to /profile/user/{username}
        return RedirectResponse(url=f"/profile/user/{username}", status_code=302)
    
    with open("app/templates/login.html") as html:
        return HTMLResponse(content=html.read())

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Validate credentials and create a new session if valid"""
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    # Check if username exists and password matches
    user = await get_user_by_username(username)
    if user is not None:
        if verify_password(password, user["password"]):
            pass
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a new session
    session_id = str(uuid.uuid4())
    await create_session(user["id"], session_id)

    # Create response with:
    #   - redirect to /profile/user/{username}
    #   - set cookie with session ID
    #   - return the response
    response = RedirectResponse(url=f"/profile/user/{username}", status_code=302)
    response.set_cookie(key="sessionId", value=session_id)
    return response

@app.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """Logout user and delete session"""
    # Get sessionId from cookies
    session_id = request.cookies.get("sessionId")

    # Check if sessionId exists and is valid
    #   - if not, redirect to /login
    current_session = await get_session(session_id)
    if current_session is None:
        return RedirectResponse(url="/login", status_code=302)

    # Delete session
    await delete_session(session_id)

    # Redirect to /login
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="sessionId")
    return response

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="0.0.0.0", port=6543, reload=False)