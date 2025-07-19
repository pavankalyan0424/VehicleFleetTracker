import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes import router

app = FastAPI()


app.include_router(router=router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
