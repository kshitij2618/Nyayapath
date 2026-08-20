from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(
    title="NyayaPath API",
    description="Local multilingual civic-rights navigator",
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "NyayaPath",
        "status": "running",
    }