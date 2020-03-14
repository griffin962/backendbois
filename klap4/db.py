from datetime import datetime
import logging
from pathlib import Path
from typing import Union
import os

import sqlalchemy
import sqlalchemy.orm

import klap4.db_entities

# Session factory that we assign when we call connect(), used as a constructor down the road.
Session = None

# Environmental variable to dictate if we reset the database or not.
env_reset = os.environ.get("KLAP4_DB_RESET", "0").lower() in ["1", "true", "yes"]

# Environmental variable to set the DB module's log level.
logging.addLevelName(9, "SQL")  # So it doesn't complain.
env_log_level = logging.getLevelName(os.environ.get("KLAP4_DB_DEBUG", "error").upper())


from klap4.db_entities.software_log import SoftwareLog
class DBHandler(logging.Handler):
    """Class to handle writing log entries into the database."""

    # Backlog to catch log entries when we are not connected to the database.
    backlog = []

    def catchup(self) -> None:
        """Catches up the handler (ideally) when we are connected to the database."""
        while len(self.backlog) > 0:
            self.emit(self.backlog[0], recursing=True)
            self.backlog.pop(0)

    def emit(self, record, *, recursing: bool = False) -> None:
        """Actually records the log entry to the database, if not connected yet then append to the end of a backlog."""
        if Session is None:
            if not recursing:
                self.backlog.append(record)
            return
        elif not recursing and len(self.backlog) > 0:
            self.catchup()

        session = Session()
        log = SoftwareLog(
            timestamp=datetime.fromtimestamp(record.created),
            tag=record.name,
            level_num=record.levelno,
            filename=record.filename,
            line_num=record.lineno,
            message=record.getMessage()
        )

        session.add(log)
        session.commit()


# db module's logger instance.
db_logger = logging.getLogger("db_logger")
db_logger.setLevel(env_log_level)
db_logger.addHandler(DBHandler())


def connect(file_path: Union[Path, str], *, reset: bool = False, sql_echo: bool = False) -> None:
    """Connects to a database.

    Args:
        file_path: The path to the database file.
        reset: If we should create/reset the database file.
        sql_echo: If we should instruct SQLAlchemy to echo out SQL statements when it reads/writes to the database.

    """
    global Session
    db_logger.debug("Initializing DB connection.")

    if Session is not None:
        db_logger.debug("DB already connected to.")
        return

    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    if not file_path.exists():
        reset = True

    db_engine = sqlalchemy.create_engine(f"sqlite:///{file_path}", echo=sql_echo)

    if reset:
        db_logger.info("Creating database.")
        file_path.unlink(missing_ok=True)
        klap4.db_entities.SQLBase.metadata.create_all(db_engine)

    Session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=db_engine))

    # Loop over every logger, check if it IS a logger (there's some placeholder types in there, and check if it has a
    # DBHandler in one of its handlers. If so, then let it catchup if it is backed up.
    for _, logger in logging.Logger.manager.loggerDict.items():
        if not isinstance(logger, logging.Logger):
            continue
        for handler in logger.handlers:
            if not isinstance(handler, DBHandler):
                continue
            handler.catchup()


# Auto-connect to database if KLAP4_DB_FILE is set.
if os.environ.get("KLAP4_DB_FILE", None) is not None:
    connect(os.environ["KLAP4_DB_FILE"], reset=env_reset, sql_echo=env_log_level == "sql")
