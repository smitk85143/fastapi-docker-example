from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    database_username: str
    database_password: str
    database_host: str
    database_port: int
    database_db: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class congig:
        env_file = '.env'

settings = Setting()