from fastapi import Request
from config import Settings

# 创建一个全局的 Settings 实例
_settings = Settings()

def get_templates(request: Request):
    return request.app.state.templates 

def get_settings():
    """
    返回应用程序配置的单例实例
    """
    return _settings 