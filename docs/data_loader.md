input: dataframe (statements along with category and account information)
output: 3 dataframes to with same schema as Transactions, Categories, accounts tables.

## steps:
1. Accounts df
	- Find unique accounts from df
	- Get all the unique accounts from the Accounts Table
	- Find any new accounts from df that are not in Accounts Table
	- If true:
		- prepare df with similar schema to Accounts table
		- append rows in df to Accounts table