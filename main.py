from contextlib import asynccontextmanager
import os
import sys

# Add the project root directory to Python path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)
# sys.path.append(project_root)

from fastapi import Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status

# from .dependencies import get_query_token, get_token_header
# from .internal import admin
from routers import article
from models.database import init_db
templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在这里初始化全局资源
    app.state.templates = templates
    init_db()
    yield
    # 清理资源

app = FastAPI(lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for error in exc.errors():
        if error.get("type") == "missing":
            field = error.get("loc")[-1]
            if field == "key":
                error_messages.append("缺少管理员密钥")
            else:
                error_messages.append(f"缺少参数: {field}")
        else:
            field = error.get("loc")[-1]
            error_messages.append(f"{field}: {error.get('msg')}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "，".join(error_messages)
        }
    )

app.include_router(article.router)


