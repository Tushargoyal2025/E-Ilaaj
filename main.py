from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers import auth, chat

app = FastAPI(title="E-Ilaaj API")


@app.on_event("startup")
def startup_event():
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

# Serve the frontend (index.html, auth.html, chat.html, css/, js/) at "/"
app.mount("/", StaticFiles(directory="static", html=True), name="static")