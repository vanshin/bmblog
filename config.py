from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str = "admin@example.com"
    items_per_user: int = 50
    db_user: str = "root"
    db_password: str = "123456"
    db_host: str = "localhost"
    db_port: str = "3306"
    db_name: str = "blog"

    @property
    def db_url(self) -> str:
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

