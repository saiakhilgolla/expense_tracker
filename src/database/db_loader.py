from sqlalchemy.orm import Session
from db_operations import AccountsInput, CRUDOperations
from db_schema import Accounts, Categories
import pandas as pd

def parse_df(df):

	accounts_df = df[["AccountType", "AccountName"]].drop_duplicates().reset_index(drop = True)
	categories_df = df[["Category"]].drop_duplicates().reset_index(drop = True)
	transactions_df = df[["date", "description", "sub_description", "transaction_type", "amount", "balance"]]

	return (accounts_df, categories_df, transactions_df)

def load_accounts_table(accounts_df, local_session: Session):
	add_accounts_crud = CRUDOperations[Accounts, AccountsInput](Accounts)
	unique_account_instances = add_accounts_crud.get_unique_records(local_session)
	unique_accounts = [account_instance.AccountName for account_instance in unique_account_instances]

	current_accounts = set(unique_accounts)
	new_accounts = set(list(df["AccountName"]))

	net_new_accounts = set(current_accounts - new_accounts)

	if not net_new_accounts:
		print("No net new accounts found. Skipping without adding ...")

	accounts_to_add = AccountsInput(account_name = df.AccountName,
								 account_type = df.Accounttype,
								 account_user = 'dummy')
	add_accounts_crud.add_records(local_session, accounts_to_add)
	print ("Added new accounts to the table.")

