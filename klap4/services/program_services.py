from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_


from klap4.db_entities import SQLBase
from klap4.db_entities.program import Program
from klap4.db_entities.program import ProgramLogEntry
from klap4.db_entities.program import ProgramSlot
#from klap4.utils.json_utils import format_object_list
from klap4.utils import *

def search_programming(p_type: str, name: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    program_list = session.query(Program) \
        .filter(
            and_(Program.type.like(p_type+'%'), Program.name.like(name+'%'))
        ) \
        .all()
    
    return format_object_list(program_list)

def display_program(prog_typ: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    info_list = []
    
    #query for program object from type and name
    u_program_objs = session.query(Program) \
        .filter(Program.type == prog_typ).all()
    program_objs = format_object_list(u_program_objs)
    
    info_list.append(program_objs)

    #query for program log given type and name
    u_program_slots = session.query(ProgramSlot) \
        .filter(ProgramSlot.program_type == prog_typ).all()
        
    program_slots = format_object_list(u_program_slots)
    info_list.append(program_slots)

    return info_list