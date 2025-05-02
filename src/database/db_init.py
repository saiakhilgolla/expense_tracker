"""Creates .db file if not already exists, and creates tables as defined in db_schema.py"""
from src.database.db_config import engine, Base

def initialize_db():
	# TODO: Add a check to see if the tables already exist.
	# TODO: Add a flag to hard delete existing tables and create new ones.
	# TODO: PRINT available tables before and after running the following command.
	#create tables
	Base.metadata.create_all(engine)
	print("Tables created successfully")

if __name__ == "__main__":
	#initialize tables
	initialize_db()
