import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import router
from app.logging_config import log_exception_event

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="SentinelOps Patient",
    description="Customer Dashboard demo application monitored by SentinelOps-AI Doctor",
    version="1.0.0"
)


# Global unhandled exception handler: logs error to logs/app.log and returns 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_payload = log_exception_event(request, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "exception_type": error_payload["exception_type"],
            "message": error_payload["message"],
            "path": error_payload["path"],
            "timestamp": error_payload["timestamp"]
        }
    )


# Include API routes
app.include_router(router)

# Mount static assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Serve frontend at root
@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
