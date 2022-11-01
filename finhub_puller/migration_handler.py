import time

from alembic import command
from alembic.config import Config

from env import ALEMBIC_INI_PATH, ALEMBIC_SCRIPT_PATH, DB_URL


def migration():
    s = 1
    while True:
        try:
            alembic_migration()
            break
        except Exception as exc:
            print(f"{exc} \n => Database not ready...")

        time.sleep(s)
        s += 1
        if s > 10:
            print("Can't communicate with DB")
            exit(1)


def alembic_migration():
    alembic_cfg = Config(ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("script_location", ALEMBIC_SCRIPT_PATH)
    alembic_cfg.set_main_option("sqlalchemy.url", DB_URL)

    # This line can be deleted in a team to keep track of the changes in the database
    command.revision(config=alembic_cfg, autogenerate=True)

    command.upgrade(config=alembic_cfg, revision="head")
