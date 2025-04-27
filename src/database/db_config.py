'''This script initializes the engine, Base and configures the session to be used for all queries to the tables'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL
database_url = "sqlite:///src/database/Expenses.db"

#create the engine
engine = create_engine(database_url, echo = True)

#initiate and configure a session to perform transactions on the database
session_factory = sessionmaker(bind=engine)
session_local = session_factory()

#Define base
Base = declarative_base()