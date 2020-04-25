#!/usr/bin/env python3

from datetime import *

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Time, Table
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


# TODO: God this table name is awful
program_type_slots_table = Table("program_type_slots_table", SQLBase.metadata,
                                 Column("program_type", String, ForeignKey("program.type")),
                                 Column("program_slot_type", String, ForeignKey("program_slot.program_type")))


class Program(SQLBase):
    __tablename__ = "program"

    type = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    description = Column(String, nullable=False)

    program_slots = relationship("klap4.db_entities.program.ProgramSlot", back_populates="programs",
                                 secondary=program_type_slots_table, cascade="save-update, merge, delete")
    program_logs = relationship("klap4.db_entities.program.ProgramLogEntry", back_populates="program",
                                primaryjoin="and_("
                                                 "Program.type == ProgramLogEntry.program_type,"
                                                 "Program.name == ProgramLogEntry.program_name"
                                            ")",
                                cascade="save-update, merge, delete")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def id(self):
        return str(self.type) + '-' + str(self.name)
    
    def __repr__(self):
        return f"<Program(type={self.type}, " \
                        f"name={self.name}, " \
                        f"description={self.description})>"


class ProgramSlot(SQLBase):
    __tablename__ = "program_slot"

    program_type = Column(String, ForeignKey("program.type"), primary_key=True)
    day = Column(Integer, primary_key=True)
    time = Column(Time, primary_key=True)

    programs = relationship("klap4.db_entities.program.Program", back_populates="program_slots",
                            secondary=program_type_slots_table, cascade="save-update, merge, delete")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ProgramSlot(program_type={self.program_type}, " \
                            f"day={self.day}, " \
                            f"time={self.time})>"


class ProgramLogEntry(SQLBase):
    __tablename__ = "program_log_entry"

    program_type = Column(String, ForeignKey("program.type"), primary_key=True)
    program_name = Column(String, ForeignKey("program.name"), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    dj = Column(String, ForeignKey("dj.id"), nullable=False)

    program = relationship("klap4.db_entities.program.Program", back_populates="program_logs",
                           primaryjoin="and_("
                                            "Program.type == ProgramLogEntry.program_type,"
                                            "Program.name == ProgramLogEntry.program_name"
                                       ")",
                           cascade="save-update, merge, delete")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ProgramLogEntry(program_type={self.program_type}, " \
                                f"program_name={self.program_.name}, " \
                                f"timestamp={self.timestamp}, " \
                                f"dj={self.dj})>"
