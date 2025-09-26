from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import router as api_router


app = FastAPI(title="Contextra API", version="0.1.0")


# CORS settings for local Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Centralized router
app.include_router(api_router)
