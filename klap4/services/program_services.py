from sqlalchemy import func, extract
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, or_


from klap4.db_entities import SQLBase
from klap4.db_entities.program import ProgramFormat, Program
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
    
    #query for program object from type and name
    program = session.query(ProgramFormat) \
        .filter_by(type = prog_typ).first()

    return program


def get_program_slots():
    from klap4.db import Session
    session = Session()

    from datetime import datetime

    tdy = datetime.today().weekday()
    tmrw = tdy + 1
    ystr = tdy - 1

    if datetime.today().weekday() == 6:
        tmrw = 0
    elif datetime.today().weekday() == 0:
        ystr = 6 

    tdy_slots = session.query(ProgramSlot) \
        .filter(ProgramSlot.day == tdy).all()
    
    ystr_slots = session.query(ProgramSlot) \
        .filter(ProgramSlot.day == ystr).all()
    
    tmrw_slots = session.query(ProgramSlot) \
        .filter(ProgramSlot.day == tmrw).all()

    program_slots = {
                        "today": format_object_list(tdy_slots),
                        "yesterday": format_object_list(ystr_slots),
                        "tomorrow": format_object_list(tmrw_slots)
    }

    for category in program_slots.items():
        for slot in category[1]:
            slot['time'] = str(slot['time'])
    
    return program_slots


def get_program_log():
    from klap4.db import Session
    session = Session()

    from datetime import datetime

    tdy = datetime.today().weekday()
    tmrw = tdy + 1
    ystr = tdy - 1

    if datetime.today().weekday() == 6:
        tmrw = 0
    elif datetime.today().weekday() == 0:
        ystr = 6

    tdy_logs = session.query(ProgramLogEntry) \
        .join(
            ProgramSlot, and_(ProgramSlot.id == ProgramLogEntry.slot_id, ProgramSlot.day == tdy)
        ) \
        .all()
    
    ystr_logs = session.query(ProgramLogEntry) \
        .join(
            ProgramSlot, and_(ProgramSlot.id == ProgramLogEntry.slot_id, ProgramSlot.day == ystr)
        ) \
        .all()    
        
    tmrw_logs = session.query(ProgramLogEntry) \
        .join(
            ProgramSlot, and_(ProgramSlot.id == ProgramLogEntry.slot_id, ProgramSlot.day == tmrw)
        ) \
        .all()

    program_log_entries = {
                            "today": format_object_list(tdy_logs),
                            "yesterday": format_object_list(ystr_logs),
                            "tomorrow": format_object_list(tmrw_logs)
    }
    

    return program_log_entries


def add_program_log(program_type, program_name, slot_id, dj_id):
    from klap4.db import Session
    session = Session()

    from datetime import datetime

    new_log = ProgramLogEntry(
                                program_type=program_type,
                                program_name=program_name,
                                slot_id=slot_id,
                                timestamp=datetime.now(),
                                dj_id = dj_id
                            )
    session.add(new_log)
    session.commit()

    return new_log


def update_program_log(program_type, program_name, slot_id, dj_id, new_name):
    from klap4.db import Session
    session = Session()

    from datetime import datetime

    session.query(ProgramLogEntry) \
        .filter(
            and_(ProgramLogEntry.program_type == program_type, ProgramLogEntry.program_name == program_name,
                 ProgramLogEntry.slot_id == slot_id, ProgramLogEntry.dj_id == dj_id)
        ) \
        .update({ProgramLogEntry.timestamp: datetime.now(), ProgramLogEntry.program_name: new_name}, synchronize_session=False)
    
    session.commit()
    
    return


def delete_program_log(program_type, timestamp, dj_id):
    from klap4.db import Session
    session = Session()

    from datetime import datetime

    session.query(ProgramLogEntry) \
        .filter(and_(ProgramLogEntry.program_type == program_type, ProgramLogEntry.timestamp == timestamp, ProgramLogEntry.dj_id == dj_id)) \
        .delete()

    session.commit()
    return