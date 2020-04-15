from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_


from klap4.db_entities import SQLBase
from klap4.db_entities.program import Program
from klap4.utils.json_utils import format_object_list

def search_programming(p_type: str, name: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    program_list = session.query(Program) \
        .filter(
            and_(Program.program_type.like(p_type+'%'), Program.name.like(name+'%'))
        ) \
        .all()
    
    return format_object_list(program_list)