from typing import Any, Optional
from abc import ABC, abstractmethod
import pandas as pd
from src.utils.file_utils import load_config


class FileProcessor(ABC):
    """This abstract class defines the methods for other file processor classes"""

    @abstractmethod
    def read_file(self) -> pd.DataFrame:
        """Reads file and returns the data in a dataframe"""
        pass

    @abstractmethod
    def validate_dataframe(self) -> pd.DataFrame:
        """Checks if the df is empty and if required cols are in df"""
        pass

    @abstractmethod
    def get_account_name(self) -> str:
        """Finds account name using file name and keywords defined in config"""
        pass

    @abstractmethod
    def add_column(self, col_name: str, col_value: Any) -> pd.DataFrame:
        """Adds a column to the dataframe"""
        pass

    @abstractmethod
    def remove_column(self, col_names: list[str]) -> pd.DataFrame:
        """Removes columns from the dataframe"""
        pass


class CSVProcessor(FileProcessor):
    """This class defines methods used to process CSV files"""

    def __init__(self, file_path: str, config: dict):
        self.file_path = file_path
        self.config = config
        self.df: Optional[pd.DataFrame] = None

    def read_file(self) -> pd.DataFrame:
        try:
            self.df = pd.read_csv(self.file_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {self.file_path}") from e
        except Exception as e:
            raise Exception(f"Exception {e} was raised") from e
        return self.df

    def validate_dataframe(self) -> pd.DataFrame:
        if self.df is None or self.df.empty:
            raise ValueError(f"Dataframe imported from path [{self.file_path}] is empty. No further processing will be done.")
        elif not all(col in self.df.columns for col in self.config['REQUIRED_COLS']):
            raise ValueError(f"One or more of the required columns {self.config['REQUIRED_COLS']} are missing.")
        return self.df

    def get_account_name(self) -> str:
        account_name = [
            account for account, keywords in self.config['ACCOUNT_KEY_WORDS'].items()
            if any(keyword in self.file_path for keyword in keywords)
        ]
        if not account_name:
            raise ValueError(f"No matching account name found for the file: {self.file_path}")
        return account_name[0]

    def add_column(self, col_name: str, col_value: Any) -> pd.DataFrame:
        if col_name in self.df.columns:
            raise ValueError(f'Column {col_name} is already present in the dataframe')
        self.df[col_name] = col_value
        return self.df

    def remove_column(self, col_names: list[str]) -> pd.DataFrame:
        self.df = self.df.drop(columns=col_names, errors='ignore')  # Avoid errors for missing columns
        return self.df

    def clean_rbc_statement(self)   -> pd.DataFrame:

        # Clean Debit and Credit columns to ensure they're numeric
        self.df['Debit'] = pd.to_numeric(self.df['Debit'].replace('[\$,]', '', regex=True), errors='coerce')
        self.df['Credit'] = pd.to_numeric(self.df['Credit'].replace('[\$,()]', '', regex=True), errors='coerce')

        # Initialize empty DataFrame with reference columns
        converted_df = pd.DataFrame(columns=self.config["REFERENCE_COLUMNS"])

        # Iterate over rows and process as per instructions
        i = 0
        while i < len(self.df):
            row = self.df.iloc[i]
            next_row = self.df.iloc[i+1] if i + 1 < len(self.df) else None

            # Format date
            date = pd.to_datetime(row['Date'], errors='coerce')
            formatted_date = date.strftime('%Y-%m-%d') if pd.notnull(date) else None

            # Determine transaction type and amount
            if pd.notnull(row['Debit']) and row['Debit'] != '':
                transaction_type = 'Debit'
                amount = round(float(row['Debit']), 2)
            else:
                transaction_type = 'Credit'
                amount = round(-float(row['Credit']), 2) if pd.notnull(row['Credit']) else 0.0

            # Prepare the row
            new_row = {
                'Filter': None,
                'Date': formatted_date,
                'Description': row['Description'],
                'Sub-description': None,
                'Status': 'posted',
                'Type of Transaction': transaction_type,
                'Amount': amount
            }

            # Check for sub-description
            if next_row is not None and pd.isna(next_row['Date']) and pd.notna(next_row['Description']):
                new_row['Sub-description'] = next_row['Description']
                i += 1  # Skip next row

            # Append to final DataFrame
            converted_df = pd.concat([converted_df, pd.DataFrame([new_row])], ignore_index=True)
            i += 1
        self.df = converted_df
        return self.df