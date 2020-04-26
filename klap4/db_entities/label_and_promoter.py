#!/usr/bin/env python3

from datetime import datetime

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Label(SQLBase):
    __tablename__ = "label"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    albums = relationship("klap4.db_entities.album.Album", back_populates="label", cascade="all")

    def __repr__(self):
        return f"<Label(id={self.id}, " \
                      f"name={self.name}, " \
                      f"url={self.url})>"


class Promoter(SQLBase):
    __tablename__ = "promoter"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    albums = relationship("klap4.db_entities.album.Album", back_populates="promoter", cascade="all")

    def __repr__(self):
        return f"<Promoter(id={self.id}, " \
                         f"name={self.name})>"
