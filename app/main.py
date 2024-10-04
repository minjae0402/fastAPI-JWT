from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from .auth import router as auth_router
from .config import settings 

app = FastAPI()

app.include_router(auth_router)

@AuthJWT.load_config
def get_config():
    return settings

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=8000)
