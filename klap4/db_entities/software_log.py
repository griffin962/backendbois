from inspect import getframeinfo, stack
from os.path import basename

from bidict import bidict

from sqlalchemy import Column, Integer, String

from klap4.db import SQLBase


class SoftwareLog(SQLBase):
    __tablename__ = "software_logs"

    LEVEL = bidict(enumerate([
        "CRITICAL",
        "ERROR",
        "WARNING",
        "INFO",
        "VERBOSE",
        "DEBUG"
    ])).inverse  # Key = 'string', LEVELS.inverse key = integer

    id = Column(Integer, primary_key=True)
    tag = Column(String)
    level = Column(Integer)
    filename = Column(String)
    line_num = Column(Integer)
    message = Column(String)

    def __init__(self, message: str, **kwargs):
        kwargs["message"] = message

        if "filename" not in kwargs:
            caller = getframeinfo(stack()[3][0])
            kwargs["filename"] = basename(caller.filename)
            kwargs["line_num"] = caller.lineno

        if "level" not in kwargs:
            kwargs["level"] = SoftwareLog.LEVEL["DEBUG"]

        if "tag" not in kwargs:
            kwargs["tag"] = "UNTAGGED"

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<SoftwareLog(id={self.id}, " \
                            f"tag={self.tag}, " \
                            f"level={SoftwareLog.LEVEL.inverse[self.level]}, " \
                            f"location={self.filename}:{self.line_num} " \
                            f"message={self.message[:20] + '...' if len(self.message) > 20 else self.message})>"
