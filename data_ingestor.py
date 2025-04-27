import os
import pandas as pd
from src.data_processing.data_processor import FileProcessorFactory, DataProcessor
from src.data_categorization.gpt_categorizer import CategorizeTransaction
from src.database.db_config import session_local
from src.utils.path_utils import get_file_list, validate_file_list
from src.utils.file_utils import load_config
from src.database.db_loader import load_accounts_table, load_categories_table, load_transactions_table

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, 'configs', 'file_config.json')
print(CONFIG_PATH)
# Load file and database paths from config
CONFIG = load_config(CONFIG_PATH)
file_paths = CONFIG['FILE_PATHS']


def process_and_categorize_files(file_path: str, required_columns: list[str]):
    """Process CSV files, categorize transactions, and insert them into the database."""
    file_processor = FileProcessorFactory.get_file_processor('csv', file_path)
    processed_df = DataProcessor(file_processor).process_file()

    # Categorize transactions by passing each row with required cols as a string to categorizer
    categories = [
        CategorizeTransaction(row.to_string()).get_category()
        for _, row in processed_df[required_columns].iterrows()
    ]
    processed_df['Category'] = categories
    return processed_df


def load_tables_to_db(df: pd.DataFrame):
    # Load Accounts
    load_accounts_table(df, session_local)

    # Load Categories
    load_categories_table(df, session_local)

    # Load Transactions
    load_transactions_table(df, session_local)


def main():
    print("called main function")

    # Get file paths for debit accounts
    print(CONFIG_PATH)
    debit_file_paths = get_file_list(CONFIG["debit_path"])
    validated_debit_file_paths = validate_file_list(debit_file_paths)

    # Get file paths for credit accounts
    credit_file_paths = get_file_list(CONFIG["credit_path"])
    validated_credit_file_paths = validate_file_list(credit_file_paths)

    # Required columns for processing
    required_columns = ["Date", "Description", "SubDescription", "TransactionType", "Amount"]

    # Process and load debit statements
    for debit_path in validated_debit_file_paths:
        debit_df = process_and_categorize_files(debit_path, required_columns)
        load_tables_to_db(debit_df)

    # Process and load credit statements
    for credit_path in validated_credit_file_paths:
        credit_df = process_and_categorize_files(credit_path, required_columns)
        load_tables_to_db(credit_df)


if __name__ == '__main__':
    main()
