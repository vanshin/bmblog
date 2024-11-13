from fastapi import Depends, FastAPI

# from .dependencies import get_query_token, get_token_header
# from .internal import admin
from .routers import article

app = FastAPI(dependencies=[Depends(get_query_token)])


app.include_router(article.router)


