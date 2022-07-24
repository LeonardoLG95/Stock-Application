from dotenv import dotenv_values

env = dotenv_values(".env")

FINHUB_TOKEN = env.get('FINHUB_API_TOKEN')

ALEMBIC_INI_PATH = env.get('ALEMBIC_INI_PATH')
ALEMBIC_SCRIPT_PATH = env.get('ALEMBIC_SCRIPT_PATH')

DB_URL = f"{env.get('DB_PROTOCOL')}://{env.get('DB_USER')}:{env.get('DB_PASSWORD')}" \
         f"@{env.get('DB_HOST')}:{env.get('DB_PORT')}/{env.get('DB_NAME')}"
