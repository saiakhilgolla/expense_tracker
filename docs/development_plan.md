## Developments and Features for v1.0.0 release

### CSV Processing:
- Change amount to Absolute amount to maintain consistency across credit and debit card transactions
- Add Balance column in the table:
	- For Debit card statements these will be non-null
	- For Credit card statements these will be NULL
- Remove MonthYear column
- Format account name
- Convert Date column to datetime
- Add function to validate CSV files
- Abstract the methods so the methods can be expanded to support other file types


**Modularization and Standardization:**
- Functions to prepare data for ingestion into tables (in the new model)
- Standardize methods to request data from this module
- Standardize the data output from this module
- Enforce table schemas before ingesting data into tables

**Debit Card Transaction Processing:**
- Come up with a strategy to identify Credit Card bill payments and ignore them from expenses
- Identify rent payments
- Strategy to ignore Dufferin rent payments from August, 2024 from expenses
- Strategy to ignore interac for Dufferin rent from income




### GPT Categorization:
- Add Error handling for chatgpt
- Add constraints to ensure consistent and accurate outputs for categories.
	- Sometimes it outputs "Category: Investment", instead of just "Investment", for example
- Separate the category list into a config file
- Add feature to find sub-category for each transaction

### Database:
- Data modeling and normalization
- Database iniitation script to create tables that align with modeling
- Functions to perform CRUD operations
- Functions to fetch data for each visualization

### Dashboard:
- Separate dashboard module
- Crete function to build dashboard layout
- Create functions to build visuals (preferably interactive visuals)

### Utils:
**File Utils:**
- Add validation functions for CSV and PDF files
- Add function to move processed files into a different folder

### Logging:
- Add module to separate logging

### Main Functions:
- Modify data_ingestor script to align with new changes

### Tests:
- write tests for individual functions in data_processing module