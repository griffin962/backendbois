from pathlib import Path
from typing import Union
import os

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base

SQLBase = declarative_base()

import klap4.db_entities

Session = None


true_vals = ["1", "true", "yes"]
env_reset = os.environ.get("KLAP4_DB_RESET", "0").lower() in true_vals
env_echo = os.environ.get("KLAP4_DB_ECHO", "0").lower() in true_vals


def connect(file_path: Union[Path, str], *, create: bool = env_reset, sql_echo: bool = env_echo):
    global Session
    print("Initializing DB connection.")

    if Session is not None:
        print("DB already connected to.")
        return

    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    if not file_path.exists():
        create = True

    db_engine = sqlalchemy.create_engine(f"sqlite:///{file_path}", echo=sql_echo)
    Session = sqlalchemy.orm.sessionmaker(bind=db_engine)

    if create:
        print("Creating database.")
        SQLBase.metadata.create_all(db_engine)


if os.environ.get("KLAP4_DB_FILE", None) is not None:
    connect(os.environ["KLAP4_DB_FILE"], create=env_reset, sql_echo=env_echo)
