from fastapi import FastAPI

from app.calls.inbound import router as inbound_router
from app.calls.outbound import router as outbound_router

app = FastAPI()

app.include_router(inbound_router)
app.include_router(outbound_router)


@app.get("/health")
def health():
    return {"status": "ok"}
