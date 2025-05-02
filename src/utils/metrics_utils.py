def get_expense_transactions(df):
    """
    Categorizes each transaction as an expense based on the following rules:

    1. Credit Card Expenses:
       - Include all debit transactions in credit cards


    2. Chequing Account Expenses:
       - Debit transactions in chequing accounts where sub_description includes: these are either subscriptions or
         credit card bill payments for cards I am not tracking yet.
         Royal Bank Visa, Remitly, Planet Fitness, American Express, Hsbc Mastercard, Hone Fitness
    """
    # Rule 1: Debit transactions in credit cards are considered expenses
    credit_card_expenses = (df['transaction_type'] == 'Debit') & (df['account_type'] == 'Credit Card')

    # Rule 2: Debit transactions in chequing accounts with specific sub_descriptions are considered expenses
    chequing_expenses = (df['transaction_type'] == 'Debit') & (df['account_type'] == 'Chequing Account') & df['sub_description'].str.contains(
        "Royal Bank Visa|Remitly|Planet Fitness|American Express|Hsbc Mastercard|Hone Fitness",
        case=False, na=False)

    # Combine both conditions for total expenses
    return credit_card_expenses | chequing_expenses

def get_credit_card_refund_transactions(df):
    """
    Categorizes credit card transactions as refunds based on below logic:
    1. Credit transactions in credit cards where description does NOT contain:
         "FROM - *****04" or "SCOTIABANK TRANSIT"
    """
    credit_card_refunds = (
        (df['transaction_type'] == 'Credit') &
        (df['account_type'] == 'Credit Card') &
        ~df['description'].str.contains("FROM - \*{5}04|SCOTIABANK TRANSIT", case=False, na=False)
    )

    return credit_card_refunds