import os

from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DB_URI = f'sqlite:////{os.environ["PWD"]}/app/db/sqlite.db'
db_engine: Engine = create_engine(DB_URI)
Session = sessionmaker(db_engine)
