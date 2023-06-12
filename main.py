import uvicorn

from .app import get_application

if __name__ == "__main__":
    uvicorn.run(get_application, host="0.0.0.0", port=8080, log_level="info")
