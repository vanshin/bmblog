from contextlib import asynccontextmanager
import os
import sys

# Add the project root directory to Python path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)
# sys.path.append(project_root)

from fastapi import Depends, FastAPI
from fastapi.templating import Jinja2Templates

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


app.include_router(article.router)


