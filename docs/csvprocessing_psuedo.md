- create abstract class for file processing:
	workflow:
	INPUT: directory path
	OUTPUT: dataframe

	FUNC get_file_paths (directory path) -> LIST[full file paths]
		- list all objects in the directory
		- IF object is file
			- join directory path and file name

	FUNC get_file_ext (file path) -> file ext
		- split the file path string with '.'
		- return the last string

	CLASS fileprocessorfactory
		FUNC get_file_processor(file path, file ext)
			IF file ext = CSV
				then csv processor (file path, file ext)
			ELIF file ext = excel
				then excel processor(file path, file ext)
			ELIF file ext = pdf
				then pdf processor(file path, file ext)

	CLASS fileprocessing
		FUNC data processor
			get_file_paths
			FOR each file path
				- get_file_ext
				- get_file_processor
				- read_file
				- validate_df
				- get_account_name
				- add_col(account name,  value)
				- add_col (account type, value)
				- if account_type = credit
					- add_col('Balance', NULL)
				- remove_col (col_name)
				- add_balance_col()

	CLASS fileprocessor
		@abstractmethod
		FUNC read_file
			pass

		@abstractmethod
		FUNC validate_dataframe
			pass

		@abstractmethod
		FUNC get_account_name
			pass

		@abstractmethod
		FUNC add_col
			pass

		@abstractmethod
		FUNC remove_col
			pass


	CLASS csvprocessor
		FUNC read_file(file path)
			return dataframe

		FUNC validate_dataframe(df)
			IF df is empty
				RAISE error
			ELIF required cols not in df_cols
				RAISE cols not found error
			ELSE
				return df

		FUNC get_account_name (file path)
			# ADD IN CONFIG: account names : {'Scotiabank Gold Amex': (Scotia, gold, amex)}
			FOR account name, keywords in account_names dictionary
				IF keywords in file path (case insensitive match)
					return account name

		FUNC add_col(DF, col_name, col_value)
			IF col_name in df.columns
				RAISE WARNING col already present
				return
			df[col name] = col_value
			return df

		FUNC remove_col(df, col_name)
			IF col_name NOT IN df.cols
				RAISE col not found
			drop col_name
			return df

		FUNC add_balance_col(df)
			IF  account type = credit
				add a balance column with NULL
			return df


----------------- --------------------- ---------------
		FUNC add_account_name(file path)
			df[accout name] = get_account_name (file path)

		FUNC add_account_type(df)
			ACCOUNT TYPE CONFIG: {account name: accout type}
			df[account type] = account type config[df.account_name]






