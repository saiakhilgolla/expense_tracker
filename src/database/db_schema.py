from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from src.database.db_config import Base


class AbstractTable(Base):
	__table__ : str
	__abstract__ = True # stops sqlalchemy from creating a table for this class

class Categories(AbstractTable):
	__tablename__ = "categories"

	#Define table schema
	id = Column(Integer, primary_key=True, nullable=False, unique=True, index=True)
	category_name = Column(String, unique=True)
	parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

	#Relationships
	transactions =  relationship("Transactions", backref= "category")

class Accounts(AbstractTable):
	__tablename__= "accounts"

	#Define table schema
	id = Column(Integer, primary_key=True, nullable=False, unique=True, index=True)
	account_name = Column(String, unique=True)
	account_type = Column(String)
	account_user = Column(String)

	#Relationship
	transactions  = relationship("Transactions", backref="account")

class Transactions(AbstractTable):
	__tablename__="transactions"

	#Define table schema
	id = Column(Integer, primary_key=True, nullable=False, unique=True)
	date = Column(Date, nullable=False)
	description = Column(String)
	sub_description = Column(String)
	transaction_type = Column(String)
	amount = Column(Float)
	balance = Column(Float)

	#Foreign Keys
	account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
	category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
