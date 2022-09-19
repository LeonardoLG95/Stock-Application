from dotenv import dotenv_values

env = dotenv_values(".env")

FINHUB_TOKEN = env.get("FINHUB_API_TOKEN")

ALEMBIC_INI_PATH = env.get("ALEMBIC_INI_PATH")
ALEMBIC_SCRIPT_PATH = env.get("ALEMBIC_SCRIPT_PATH")

DB_USER = env.get("DB_USER")
DB_PASSWORD = env.get("DB_PASSWORD")
DB_HOST = env.get("DB_HOST")
DB_PORT = env.get("DB_PORT")
DB_NAME = env.get("DB_NAME")

DB_URL = (
    f"{env.get('DB_PROTOCOL')}://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
