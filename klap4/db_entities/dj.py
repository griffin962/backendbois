#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class DJ(SQLBase):
    __tablename__ = "dj"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False)

    def __init__(self, **kwargs):
        if "is_admin" not in kwargs:
            kwargs["is_admin"] = False
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<DJ(id={self.id}, " \
                   f"name={self.name}, " \
                   f"is_admin={self.is_admin})>"
