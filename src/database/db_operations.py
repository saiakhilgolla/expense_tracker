from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import Optional, TypeVar, Generic, Type, Union, List

# Class to enforce input schema before adding data into Transactions table
class TransactionsInput(BaseModel):
    date: date
    description: str
    sub_description: str
    transaction_type: str
    amount: float
    balance: float
    account_id: int
    category_id: int

# Class to enforce input schema before adding input into Accounts table
class AccountsInput(BaseModel):
    account_name: str
    account_type: str
    account_user: Optional[str] = None

# Class to enforce input schema before adding input into Categories table
class CategoryInput(BaseModel):
    category_name: str
    parent_id: Optional[str] = None

# Define types for model and schema
ModelType = TypeVar("ModelType")
SchemaType = TypeVar("InputSchema", bound=BaseModel)

# Class to define CRUD operations
class CRUDOperations(Generic[ModelType, SchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def add_records(self, local_session: Session, input_objs: Union[SchemaType, List[SchemaType]]):
        """Add one or more records to the table."""
        if isinstance(input_objs, list):
            model_instances = [self.model(**obj.model_dump()) for obj in input_objs]
            local_session.add_all(model_instances)
            local_session.commit()
            for instance in model_instances:
                local_session.refresh(instance)
            return model_instances
        else:
            model_instance = self.model(**input_objs.model_dump())
            local_session.add(model_instance)
            local_session.commit()
            local_session.refresh(model_instance)
            return model_instance

    def delete_records(self, local_session: Session, id: int):
        """Delete a record by ID."""
        model_instance = local_session.query(self.model).filter(self.model.id == id).first()
        if model_instance:
            local_session.delete(model_instance)
            local_session.commit()

    def update(self, local_session: Session, id: int, update_input: dict):
        """Validate and update an existing record."""
        model_instance = local_session.query(self.model).filter(self.model.id == id).first()
        if model_instance:
            for field, value in update_input.items():
                setattr(model_instance, field, value)
            local_session.commit()
            local_session.refresh(model_instance)
        return model_instance

    def get_unique_records(self, local_session: Session) -> List:
        """Retrieve distinct records based on unique column."""
        unique_column = None
        if self.model.__name__ == "Accounts":
            unique_column = "account_name"
        elif self.model.__name__ == "Categories":
            unique_column = "category_name"

        if unique_column:
            return local_session.query(getattr(self.model, unique_column)).distinct().all()
        return []

    def get_records(self, local_session: Session):
        """Get all records from table"""
        return local_session.query(self.model).all()
