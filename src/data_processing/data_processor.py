import numpy as np
from src.data_processing.file_processors import FileProcessor, CSVProcessor
from src.utils.file_utils import load_config


config = load_config("config/file_config.json")

class FileProcessorFactory:
	"""This class assigns appropriate file processor depending on file type"""

	@staticmethod
	def get_file_processor(file_type:str, file_path:str) -> FileProcessor:
		if file_type == 'csv':
			return(CSVProcessor(file_path))
		else:
			raise ValueError(f"File type {file_type} not supported")



class DataProcessor():
	"""This class orchestrates the file parsing, transformation and cleaning steps
	"""
	def __init__(self, file_processor:FileProcessor):
		self.file_processor = file_processor

	def process_file(self):
		#step1: read file and output a dataframe
		df = self.file_processor.read_file()

		#Validate dataframe
		df = self.file_processor.validate_dataframe()

		#Get account name
		account_name = self.file_processor.get_account_name()

		#Add Account name column
		df = self.file_processor.add_column("AccountName", account_name)

		#Add Account type column
		account_type = [account_type for account_name, account_type in config['ACCOUNT_TYPES'] if account_name == df.AccountName][0]
		df = self.file_processor.add_column("AccountType", account_type)

		#Add "Balance" column to credit card
		if df.AccountType[0] == "Credit Card":
			df = self.file_processor.add_column("Balance", np.nan)

		#Remove unnecessary columns
		if df.AccountType[0] == "Credit Card":
			df = self.file_processor.remove_column(["Filter", "Status"])
		else:
			df = self.file_processor.remove_column("Filter")

		return(df)






