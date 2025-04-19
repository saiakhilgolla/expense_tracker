from sqlalchemy.orm import Session
from db_operations import AccountsInput, CategoryInput, TransactionsInput, CRUDOperations
from db_schema import Accounts, Categories, Transactions
import pandas as pd


def load_accounts_table(df, local_session: Session):
    add_accounts_crud = CRUDOperations[Accounts, AccountsInput](Accounts)

    # Get current accounts from DB
    unique_account_instances = add_accounts_crud.get_unique_records(local_session)
    current_accounts = {account_instance[0] for account_instance in unique_account_instances}

    # Get unique accounts from DataFrame
    new_accounts = set(df["AccountName"].unique())

    # Find net new accounts
    net_new_accounts = new_accounts - current_accounts

    if not net_new_accounts:
        print("No net new accounts found. Skipping without adding ...")
        return

    # Filter and prepare new records
    records_to_add = []

    for account_name in net_new_accounts:
        row = df[df["AccountName"] == account_name].iloc[0]  # Pick first matching row
        new_account = AccountsInput(
            account_name=account_name,
            account_type=row["Accounttype"],
            account_user="dummy"
        )
        records_to_add.append(new_account)

    # Add records to DB
    add_accounts_crud.add_records(local_session, records_to_add)
    print("Added new accounts to the table.")


def load_categories_table(df, local_session: Session):
    add_categories_crud = CRUDOperations[Categories, CategoryInput](Categories)

    # Get current categories from DB
    unique_category_instances = add_categories_crud.get_unique_records(local_session)
    current_categories = {category_instance[0] for category_instance in unique_category_instances}

    # Get unique categories from DataFrame
    new_categories = set(df["Category"].unique())

    # Find net new categories
    net_new_categories = new_categories - current_categories

    if not net_new_categories:
        print("No net new categories found. Skipping without adding ...")
        return

    # Filter and prepare new records
    records_to_add = []

    for category in net_new_categories:
        new_category = CategoryInput(
            category=category
        )
        records_to_add.append(new_category)

    # Add records to DB
    add_categories_crud.add_records(local_session, records_to_add)
    print("Added new categories to the table.")


def load_transactions_table(df, local_session: Session):
    add_transactions_crud = CRUDOperations[Transactions, TransactionsInput](Transactions)

	# Create Account ID mappings
    account_lookup = {
        account.account_name: account.id
		for account in local_session.query(Accounts).all()
	}

	# Create Category ID mappings
    category_lookup = {
        category.category_name : category.id
        for category in local_session.query(Categories).all()
	}

	# Create Transaction instances to load
    records_to_add = []
    for index, row in df.iterrows():
        new_transaction = TransactionsInput(
            "date": row["Date"],
            "description": row["Description"],
            "sub_description": row[SubDescription],
            "transaction_type" row["TransactionType"],
            "amount": row["Amount"],
            "balance": row["Balance"],
            "account_id": account_lookup.get(row["AccountName"]),
            "category_id": category_lookup.get(row["Category"])
		)
        records_to_add.append(new_transaction)

    # Add records to DB
    add_transactions_crud.add_records(local_session, records_to_add)
    print("Added new categories to the table.")