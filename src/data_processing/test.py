import pandas as pd

# Hardcoded column names based on the reference file
reference_columns = [
    'Filter',
    'Date',
    'Description',
    'Sub-description',
    'Status',
    'Type of Transaction',
    'Amount'
]

# Read the example file
df_example = pd.read_csv("data/credit_accounts/rbc_jan_to_april2025.csv")

# Clean Debit and Credit columns to ensure they're numeric
df_example['Debit'] = pd.to_numeric(df_example['Debit'].replace('[\$,]', '', regex=True), errors='coerce')
df_example['Credit'] = pd.to_numeric(df_example['Credit'].replace('[\$,()]', '', regex=True), errors='coerce')

# Initialize empty DataFrame with reference columns
converted_df = pd.DataFrame(columns=reference_columns)

# Iterate over rows and process as per instructions
i = 0
while i < len(df_example):
    row = df_example.iloc[i]
    next_row = df_example.iloc[i+1] if i + 1 < len(df_example) else None

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

# Save to CSV
converted_df.to_csv("data/credit_accounts/final_cleaned_converted.csv", index=False)
