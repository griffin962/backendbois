import datetime
from inspect import getframeinfo, stack
import logging
from os.path import basename

from sqlalchemy import Column, Integer, String, DateTime

from klap4.db_entities import SQLBase


class SoftwareLog(SQLBase):
    __tablename__ = "software_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    tag = Column(String, nullable=False)
    level = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    line_num = Column(Integer, nullable=False)
    message = Column(String, nullable=False)

    def __init__(self, message: str, **kwargs):
        kwargs["message"] = message

        if "filename" not in kwargs:
            caller = getframeinfo(stack()[3][0])
            kwargs["filename"] = basename(caller.filename)
            kwargs["line_num"] = caller.lineno

        if "level" not in kwargs:
            kwargs["level"] = logging.getLevelName("debug")

        if "tag" not in kwargs:
            kwargs["tag"] = "UNTAGGED"

        if "timestamp" not in kwargs:
            kwargs["timestamp"] = datetime.datetime.now()

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<SoftwareLog(id={self.id}, " \
                            f"{self.timestamp=}" \
                            f"{self.tag=}, " \
                            f"{self.level=}, " \
                            f"location={self.filename}:{self.line_num} " \
                            f"message={self.message[:20] + '...' if len(self.message) > 20 else self.message})>"
