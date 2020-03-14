from sqlalchemy.ext.declarative import declarative_base

# Base SQLAlchemy ORM class.
SQLBase = declarative_base()

# Need to append new modules as we add them in this file.
from klap4.db_entities.software_log import *
from klap4.db_entities.artist import *
from klap4.db_entities.genre import *
