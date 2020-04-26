from sqlalchemy import func, extract
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, or_


from klap4.db_entities import SQLBase
from klap4.db_entities.program import Program
from klap4.db_entities.program import ProgramLogEntry
from klap4.db_entities.program import ProgramSlot
from klap4.utils.json_utils import format_object_list

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


def get_program_slots():
    from klap4.db import Session
    session = Session()

    from datetime import datetime

    tdy = datetime.today().weekday()
    tmrw = tdy + 1
    ystr = tdy - 1

    if datetime.today().weekday() == 6:
        tmrw = 0
    elif datetime.today().weekday == 0:
        ystr = 6 

    tdy_slots = session.query(ProgramSlot) \
        .filter(ProgramSlot.day == tdy)
    
    ystr_slots = session.query(ProgramSlot) \
        .filter(ProgramSlot.day == ystr)
    
    tmrw_slots = session.query(ProgramSlot) \
        .filter(ProgramSlot.day == tmrw)

    program_slots = tdy_slots.union(ystr_slots).union(tmrw_slots).all() 
    
    return format_object_list(program_slots)


def get_program_log():
    from klap4.db import Session
    session = Session()

    from datetime import datetime

    tdy = datetime.today().weekday()
    tmrw = tdy + 1
    ystr = tdy - 1

    if datetime.today().weekday() == 6:
        tmrw = 0
    elif datetime.today().weekday == 0:
        ystr = 6 

    tdy_logs = session.query(ProgramLogEntry) \
        .filter(extract('day', ProgramLogEntry.timestamp) == tdy)    

    ystr_logs = session.query(ProgramLogEntry) \
        .filter(extract('day', ProgramLogEntry.timestamp) == ystr)

    tmrw_logs = session.query(ProgramLogEntry) \
        .filter(extract('day', ProgramLogEntry.timestamp) == tmrw)
    
    program_log_entries = tdy_logs.union(ystr_logs).union(tmrw_logs).all()

    return format_object_list(program_log_entries)