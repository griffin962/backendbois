#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Program(SQLBase):
    __tablename__ = "program"

    program_type = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    description = Column(String, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def id(self):
        return str(self.program_type) + str(self.name)
    
    def __repr__(self):
        return f"<Program(program_type={self.program_type}, " \
                        f"name={self.name}, " \
                        f"description={self.description})>"