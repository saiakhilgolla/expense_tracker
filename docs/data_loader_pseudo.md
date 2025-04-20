workflow:
- Identify unique values in AccountName and Category column
- Check if AccountName is already in the account_name table
	- if YES, ignore
	- if NO, add account name in account_name table
- Repeat this for category table
- replace AccountName and Category column values in df with PK from account_name and category tables
- ingest data


FUNC get_unique_values(df, col_name)
	df[col_name].uniques

account_name_uniques = get_unique_values(df, AccountName)
category_uniques = get_unique_values(df, Category)

fetch account names from account_name table
fetch categories from Category table

if account_name_uniques in account names -> ignore
else  add account_name to new_accounts_df

if category_uniques in categories -> ignore
else add category to new_category_df

replace AccountName and Category columns with their PKs from account_name and category tables

ingest transactions_df to transactions tables
new_accounts_df to accounts table
new_category_df to category table
