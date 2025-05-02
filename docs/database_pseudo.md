## setup database
	Initialize session to connect and communicate with DB

## Set up the model
	- class category
		- define a class to create table, columns and table relationship
			- Columns:
				- Category ID - Integer - Primary Key - Unique - Non Null
				- Category/Sub-Category Name - String - Unique
				- Parent Category ID - Integer
			- Relationships:
				- one-to-many relationship with Transactions table
		- **Add an index to category ID??**


	- class accounts
		- define a class to create table, columns and table relationship
			- Columns:
				- Account ID - Integer - Primary Key - Unique - Non Null
				- Account Name - String - Unique
				- Account Type - String
				- Account User - String
			- Relationships:
				- one-to-many relationship with Transactions table
		- **Add an index to category ID??**


	- class transactions
		- define a class to create table, columns and table relationship
			- Columns:
				- Transaction ID - Integer - Unique - Primary Key - Non Null
				- Account ID - Integer - Foreign Key
				- Date - Date - Non Null
				- Description - String
				- SubDescription - String
				- TransactionType - String
				- Amount - Float
				- Balance - Float
				- Category ID - Integer - Foreign Key
			- Relationships:
				- many-to-one relationship with accounts table
				- many-to-one relationship with category table


## functions to perfrom crud operations on db
transactions Input
accounts input
categories input


CLASS CRUDOperations(Generic[model, schema]):
	def add_records ():

	def delete_records():

	def update_records():


add transaction
get transactions
update transaction
delete transaction

add account
get account
update account
delete account

add category
get category
update category
delete category

## Prepare data for ingesting into tables
	- FUNC check_new_categories
		- get_categories
		- if unique categories not in get_categories
			- insert_new_category
		- else:
			ignore