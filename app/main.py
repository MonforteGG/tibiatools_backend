from app.api import router as api_router
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware



print("Tibia Loot API Started!")

app = FastAPI()

app.include_router(api_router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    print("Time took to process the request and return response is {} sec".format(time.time() - start_time))
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚡ O puedes poner ["http://localhost:4200"] si quieres más seguro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
