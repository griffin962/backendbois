#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Program(SQLBase):
    __tablename__ = "program"

    program_type = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    description = Column(String, nullable=False)

    program_slots = relationship("klap4.db_entities.program.ProgramSlot", back_populates="program")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def id(self):
        return str(self.program_type) + '+' + str(self.name)
    
    def __repr__(self):
        return f"<Program(program_type={self.program_type}, " \
                        f"name={self.name}, " \
                        f"description={self.description})>"


class ProgramSlot(SQLBase):
    __tablename__ = "program_slot"

    program_type = Column(String, ForeignKey("program.program_type"), primary_key=True)
    day = Column(Integer, primary_key=True)
    time = Column(DateTime, primary_key=True)

    program = relationship("klap4.db_entities.program.Program", back_populates="program_slots")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def id(self):
        return str(self.program_type) + str(self.day) + str(self.time)
    
    def __repr__(self):
        return f"<ProgramSlot(program_type={self.program_type}, " \
                    f"day={self.day}, time={self.time})>"


class ProgramLogEntry(SQLBase):
    __tablename__ = "program_log_entry"

    program_type = Column(String, ForeignKey("program.program_type"), primary_key=True)