from typing import Optional
from openai import OpenAI
import os
from src.utils.file_utils import load_config
import json

config = load_config("config/categories.json")

class CategorizeTransaction:
    def __init__(self, txn: str, api_key: Optional[str] = None):
        self.transaction = txn
        self.api_key = api_key

    def initialize_chatgpt(self):
        # Check if API key is provided or available in environment variables
        if (os.getenv('OPENAI_API_KEY') or self.api_key) is None:
            raise ValueError("API key is required to initialize OpenAI client.")

        # If API key not found in environmental variables, assign API key.
        if os.getenv('OPENAI_API_KEY') is None:
            return OpenAI(api_key=self.api_key)

        return OpenAI()

    def build_prompt(self) -> str:
        return f"Transaction: {self.transaction}"

    def get_category(self) -> str:
        client = self.initialize_chatgpt()
        prompt = self.build_prompt()

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "developer", "content": """
                    Imagine yourself as a financial assistant and your job is to categorize each transaction to enrich the data.
                    Just provide the category name for each transaction from the following category list.
                    Groceries
                    Dining and Restaurants
                    Transportation
                    Shopping
                    Travel
                    Entertainment
                    Utilities
                    Health and Fitness
                    Subscriptions and Memberships
                    Education
                    Insurance
                    Investments and Savings
                    Income or Salary
                    Miscellaneous
                    Personal and Household Expenses"""},
                    {"role": "user", "content": prompt}
                ]
            )
            return self.clean_category(completion.choices[0].message.content.strip())
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def clean_category(gpt_category: str):
        categories = config['Categories']
        return [category for category in categories if category in gpt_category][0]

# Example Usage
"""
txn = "2024-11-15, Investment, Wealthsimple Investments Inc., Debit, -1300"
categorizer = CategorizeTransaction(txn)

category = categorizer.get_category()
print(category)
"""

# TODO: ADD FUNCTIONS TO RECATEGORIZE CERTAIN TRANSACTIONS AND TRAIN CHATGPT
