import mysql.connector
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uvicorn
import os

app = FastAPI()

@app.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}

@app.post("/tempdata")
async def tempdata(request: Request):
    data = await request.json()
    temp = data.get("temp")
    return {"message": "Data received", "data": temp}

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="0.0.0.0", port=6543, reload=False)