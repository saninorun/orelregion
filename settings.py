from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str = Field(validation_alias='DB_HOST') 
    db_port: str = Field(validation_alias='DB_PORT')
    db_name: str = Field(validation_alias='DB_NAME')
    db_user: str = Field(validation_alias='DB_USER')
    db_passw: str = Field(validation_alias='DB_PASSW')

    server_port: int = Field(validation_alias='SERVER_PORT') 
    server_host: str = Field(validation_alias='SERVER_HOST') 
   
    model_config = SettingsConfigDict( 
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='allow'
        )


settings = Settings()