from fastapi import Request
from config import Settings

def get_templates(request: Request):
    return request.app.state.templates 

def get_db_settings():
    return Settings()