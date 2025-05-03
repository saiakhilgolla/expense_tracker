import numpy as np
import pandas as pd
from src.data_processing.file_processors import FileProcessor, CSVProcessor
from src.utils.file_utils import load_config

config = load_config("config/file_config.json")


class FileProcessorFactory:
    """This class assigns appropriate file processor depending on file type"""

    @staticmethod
    def get_file_processor(file_type: str, file_path: str, config: dict) -> FileProcessor:
        if file_type == 'csv':
            return CSVProcessor(file_path, config)
        else:
            raise ValueError(f"File type {file_type} not supported")


class DataProcessor:
    """This class orchestrates the file parsing, transformation and cleaning steps"""

    def __init__(self, file_processor: FileProcessor):
        self.file_processor = file_processor

    def process_file(self, config: dict) -> pd.DataFrame:
        # Step 1: read file and output a DataFrame
        df = self.file_processor.read_file()

        # Get account name
        account_name = self.file_processor.get_account_name()

        # Parse RBC statements
        if "RBC" in account_name:
            df = self.file_processor.clean_rbc_statement()

        # Validate DataFrame
        df = self.file_processor.validate_dataframe()

        # Add AccountName column
        df = self.file_processor.add_column("AccountName", account_name)

        # Add AccountType column
        account_type = [
            account_type
            for acct_name, account_type in config['ACCOUNT_TYPES'].items()
            if acct_name == df.AccountName[0]
        ][0]
        df = self.file_processor.add_column("AccountType", account_type)

        # Add "Balance" column to credit card accounts
        if df.AccountType[0] == "Credit Card":
            df = self.file_processor.add_column("Balance", np.nan)

        # Remove unnecessary columns
        if df.AccountType[0] == "Credit Card":
            df = self.file_processor.remove_column(["Filter", "Status"])
        else:
            df = self.file_processor.remove_column("Filter")

        return df
