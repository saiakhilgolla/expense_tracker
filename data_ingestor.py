import os
import sys
import pandas as pd

# Add src/ to path if keeping src. imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_processing.data_processor import FileProcessorFactory, DataProcessor
from src.data_categorization.gpt_categorizer import CategorizeTransaction
from src.database.db_config import session_local
from src.database.db_init import initialize_db
from src.utils.path_utils import get_file_list, validate_file_list
from src.utils.file_utils import load_config
from src.database.db_loader import load_accounts_table, load_categories_table, load_transactions_table

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'file_config.json')

CONFIG = load_config(CONFIG_PATH)

def process_and_categorize_files(file_path: str, required_columns: list[str], config: dict):
    file_processor = FileProcessorFactory.get_file_processor('csv', file_path, config)
    processed_df = DataProcessor(file_processor).process_file(config)

    print("Finished processing file.")
    print("Identifying Categories to processed transactions.....")

    categories = [
        CategorizeTransaction(row.to_string()).get_category()
        for _, row in processed_df[required_columns].iterrows()
    ]
    processed_df['Category'] = categories
    print(processed_df)
    print("Categories added to transactions data. Returning dataframe ...")
    return processed_df

def load_tables_to_db(df: pd.DataFrame):
    print("Loading Accounts information to Accounts table....")
    load_accounts_table(df, session_local)

    print("Finished loading Accounts table. Loading Categories table now.... ")
    load_categories_table(df, session_local)

    print("Finished loading Categores table. Loading Transactions table now...")
    load_transactions_table(df, session_local)

    print(f"Finished loading transactions table for month:{df.Date[0]} ")
    return

def main():
    print("Called main function.......")

    debit_file_paths = get_file_list(CONFIG["FILE_PATHS"]["DEBIT_PATH"])
    validated_debit_file_paths = validate_file_list(debit_file_paths)

    credit_file_paths = get_file_list(CONFIG["FILE_PATHS"]["CREDIT_PATH"])
    validated_credit_file_paths = validate_file_list(credit_file_paths)

    required_columns = ["Date", "Description", "Sub-description", "Type of Transaction", "Amount"]

    # Initialize DB tables
    print("Creating tables .... ")
    initialize_db()

    print("Start processing debit statements.....")

    for debit_path in validated_debit_file_paths:
        print(f"Processing file: {debit_path}..")
        if not debit_path.endswith(".csv"):
            continue
        debit_df = process_and_categorize_files(debit_path, required_columns, CONFIG)
        load_tables_to_db(debit_df)

    print("Start processing Credit statements...")

    for credit_path in validated_credit_file_paths:
        print(f"Processing file: {credit_path}..")
        if not credit_path.endswith(".csv"):
            continue
        credit_df = process_and_categorize_files(credit_path, required_columns, CONFIG)
        load_tables_to_db(credit_df)

if __name__ == '__main__':
    main()
