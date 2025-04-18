from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import Optional, TypeVar, Generic, Type


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
    account_user: str

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

    def add_records(self, local_session: Session, input_obj: SchemaType):
        """Add a new record to the table."""
        model_instance = self.model(**input_obj.model_dump())
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
        return

    def update(self, local_session: Session, id: int, update_input: dict):
        """Validate and update an existing record."""
        # Find the model instance/row to update using ID
        model_instance = local_session.query(self.model).filter(self.model.id == id).first()
        if model_instance:
            # Update columns/attributes in the model
            for field, value in update_input.items():
                setattr(model_instance, field, value)
            local_session.commit()
            local_session.refresh(model_instance)
        return model_instance

    def get_unique_records(self, local_session: Session):
        """Retrieve distinct records based on unique column."""
        unique_column = None
        if self.model.__name__ == "Accounts":
            unique_column = "account_name"
        elif self.model.__name__ == "Categories":
            unique_column = "category_name"

        if unique_column:
            return local_session.query(getattr(self.model, unique_column)).distinct().all()
        return []
