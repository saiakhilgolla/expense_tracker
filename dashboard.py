# Install these if you haven't:
# pip install streamlit pandas sqlalchemy plotly

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from src.utils.metrics_utils import get_expense_transactions, get_credit_card_refund_transactions

# -------------------------------------------
# Load Data
# -------------------------------------------
@st.cache_data
def load_data():
    # Connect to your database
    engine = create_engine('sqlite:///src/database/Expenses.db')

    # SQL JOIN: transactions + accounts + categories
    query = """
    SELECT
        t.id AS transaction_id,
        t.date,
        t.description,
        t.sub_description,
        t.transaction_type,
        t.amount,
        a.account_name,
        a.account_type,
        c.category_name
    FROM transactions t
    LEFT JOIN accounts a ON t.account_id = a.id
    LEFT JOIN categories c ON t.category_id = c.id
    """

    df = pd.read_sql_query(query, con=engine)

    # Convert date column to datetime if needed
    df['date'] = pd.to_datetime(df['date'])

    return df

# -------------------------------------------
# Streamlit App
# -------------------------------------------
st.set_page_config(page_title="Expense Tracker Dashboard", layout="wide")

st.title("💸 Expense Tracker Dashboard (with Accounts & Categories)")

# Load the data
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# -------------------------------------------
# Apply absolute values for amounts
# -------------------------------------------
df['amount'] = df.apply(
    lambda row: abs(row['amount']),
    axis=1
)

# -------------------------------------------
# Sidebar Filters
# -------------------------------------------
st.sidebar.header("Filter Transactions")

# Date Range Filter
date_min = df['date'].min()
date_max = df['date'].max()
date_range = st.sidebar.date_input("Select date Range", [date_min, date_max])

# Category Filter
categories = df['category_name'].dropna().unique()
selected_categories = st.sidebar.multiselect("Select Categories", categories, default=categories)

# Account Filter
accounts = df['account_name'].dropna().unique()
selected_accounts = st.sidebar.multiselect("Select Accounts", accounts, default=accounts)

# Transaction Type Filter
transaction_types = df['transaction_type'].dropna().unique()
selected_types = st.sidebar.multiselect("Select Transaction Types", transaction_types, default=transaction_types)

# Apply Filters
filtered_df = df[
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1])) &
    (df['category_name'].isin(selected_categories)) &
    (df['account_name'].isin(selected_accounts)) &
    (df['transaction_type'].isin(selected_types))
]

# -------------------------------------------
# Key Metrics
# -------------------------------------------
st.subheader("Key Metrics")

# Use the get_expense_transactions function to identify expense transactions
expenses = get_expense_transactions(filtered_df)
refunds = get_credit_card_refund_transactions(filtered_df)

# Total Spent: Only Debit transactions in Credit Cards and the defined expenses from Chequing Accounts
total_spent = filtered_df[expenses]['amount'].sum() - filtered_df[refunds]['amount'].sum()


# Total earned is calculated by summing just the Payroll Deposits in chequing account
total_earned = filtered_df[
    (filtered_df['transaction_type'] == 'Credit') &
    (filtered_df['description'].str.contains("Payroll Deposit", case=False, na=False))
]['amount'].sum()


col1, col2 = st.columns(2)
col1.metric("Total Spent (since Jan 2024)", f"${total_spent:,.2f}")
col2.metric("Total Earned (since Jan 2024)", f"${total_earned:,.2f}")



# -------------------------------------------
# Charts
# -------------------------------------------
st.subheader("Spending Overview")

# Monthly Total Expense Trend by Account
monthly_by_account = (
    filtered_df[expenses]
    .groupby([pd.Grouper(key='date', freq='M'), 'account_name'])['amount']
    .sum()
    .reset_index()
)
monthly_by_account['date'] = monthly_by_account['date'].dt.to_period('M').dt.to_timestamp()
monthly_by_account['month_str'] = monthly_by_account['date'].dt.strftime('%b %Y')

# Total monthly expense across accounts
monthly_total = (
    filtered_df[expenses]
    .groupby(pd.Grouper(key='date', freq='M'))['amount']
    .sum()
    .reset_index()
)
monthly_total['date'] = monthly_total['date'].dt.to_period('M').dt.to_timestamp()
monthly_total['month_str'] = monthly_total['date'].dt.strftime('%b %Y')
monthly_total['rolling_avg'] = monthly_total['amount'].rolling(window=3).mean()
avg_expense = monthly_total['amount'].mean()

# Create Plotly Figure
fig = go.Figure()

# Account-wise lines
for account in monthly_by_account['account_name'].unique():
    temp_df = monthly_by_account[monthly_by_account['account_name'] == account]
    fig.add_trace(go.Scatter(
        x=temp_df['month_str'],
        y=temp_df['amount'],
        mode='lines+markers',
        name=f"{account} Expenses",
        line=dict(width=1)
    ))

# Total expense line
fig.add_trace(go.Scatter(
    x=monthly_total['month_str'],
    y=monthly_total['amount'],
    mode='lines+markers',
    name='Total Monthly Expense',
    line=dict(color='orange', width=3)
))

# Rolling average line
fig.add_trace(go.Scatter(
    x=monthly_total['month_str'],
    y=monthly_total['rolling_avg'],
    mode='lines',
    name='3-Month Rolling Avg',
    line=dict(color='blue', dash='dash')
))

# Average expense line
fig.add_trace(go.Scatter(
    x=monthly_total['month_str'],
    y=[avg_expense] * len(monthly_total),
    mode='lines',
    name='Yearly Average Expense',
    line=dict(color='green', dash='dot')
))

# Update layout
fig.update_layout(
    title="Monthly Total Expenses by Account",
    xaxis_title="Month",
    yaxis_title="Total Expenses ($)",
    legend_title="Legend",
    height=550
)

st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------
# Monthly Payroll Income Bar Chart with Yearly Average
# -------------------------------------------
st.subheader("Monthly Payroll Income")

# Filter only Payroll Deposit credits in Chequing Accounts
payroll_df = filtered_df[
    (filtered_df['transaction_type'] == 'Credit') &
    (filtered_df['account_type'] == 'Chequing Account') &
    (filtered_df['description'].str.contains("Payroll Deposit", case=False, na=False))
]

# Group by month
monthly_income = (
    payroll_df.groupby(pd.Grouper(key='date', freq='M'))['amount']
    .sum()
    .reset_index()
)
monthly_income['month'] = monthly_income['date'].dt.strftime('%b %Y')

# Calculate yearly average
yearly_avg = monthly_income['amount'].mean()

# Create bar chart
fig_income = px.bar(
    monthly_income,
    x='month',
    y='amount',
    title="Monthly Payroll Income",
    labels={'amount': 'Income ($)', 'month': 'Month'},
    text_auto='.2s'
)

# Add yearly average line
fig_income.add_hline(
    y=yearly_avg,
    line_dash="dash",
    line_color="green",
    annotation_text=f"Yearly Avg: ${yearly_avg:,.2f}",
    annotation_position="top left"
)

fig_income.update_layout(xaxis_title="Month", yaxis_title="Income ($)")
st.plotly_chart(fig_income, use_container_width=True)

# -------------------------------------------
# Spending Breakdown by Category (Monthly) - Bar Chart
# -------------------------------------------
st.subheader("Spending Breakdown by Category (Bar Chart)")

# Prepare monthly category expenses
monthly_category_expense = (
    filtered_df[(filtered_df['transaction_type'] == 'Debit') &
                (filtered_df['account_type'] == 'Credit Card')]
    .groupby([pd.Grouper(key='date', freq='M'), 'category_name'])['amount']
    .sum()
    .reset_index()
)

# Add month_start column for filtering
monthly_category_expense['month_start'] = monthly_category_expense['date'].dt.to_period('M').dt.to_timestamp()
available_months = sorted(monthly_category_expense['month_start'].unique())
available_months_dt = [ts.to_pydatetime() for ts in available_months]

# Add month-year multiselect filter
selected_months = st.multiselect(
    "Select Months",
    options=available_months_dt,
    default=available_months_dt,
    format_func=lambda x: x.strftime('%b %Y')
)

# Filter data based on selected months
selected_month_df = monthly_category_expense[
    monthly_category_expense['month_start'].isin(pd.to_datetime(selected_months))
].copy()

# Display warning if no data is selected
if selected_month_df.empty:
    st.warning("Please select at least one month to display the breakdown.")
else:
    # Aggregate across selected months by category
    category_summary = (
        selected_month_df
        .groupby('category_name')['amount']
        .sum()
        .reset_index()
        .sort_values(by='amount', ascending=False)
    )

    # Add percentage column
    total_amount = category_summary['amount'].sum()
    category_summary['percent'] = category_summary['amount'] / total_amount * 100

    # Create horizontal bar chart
    bar_fig = px.bar(
        category_summary,
        x='amount',
        y='category_name',
        orientation='h',
        text=category_summary.apply(lambda row: f"${row['amount']:,.2f} ({row['percent']:.1f}%)", axis=1),
        labels={'amount': 'Amount ($)', 'category_name': 'Category'},
        title="Spending Breakdown by Category - Selected Months",
    )

    bar_fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    bar_fig.update_traces(textposition='outside')

    # Plot bar chart
    st.plotly_chart(bar_fig, use_container_width=True)

# -------------------------------------------
# Transactions Table (Debit and Credit)
# -------------------------------------------
st.subheader("Transactions (Debit and Credit)")

# Extract month-year and create a proper datetime column for sorting
filtered_df['month_year'] = pd.to_datetime(filtered_df['date']).dt.to_period('M').dt.to_timestamp()
filtered_df['month_year_str'] = filtered_df['month_year'].dt.strftime('%b, %Y')

# Get unique months sorted in reverse chronological order
unique_months = (
    filtered_df[['month_year', 'month_year_str']]
    .drop_duplicates()
    .sort_values('month_year', ascending=False)
)['month_year_str'].tolist()

# Unique values for filters
table_account_names = filtered_df['account_name'].dropna().unique().tolist()
table_transaction_types = filtered_df['transaction_type'].dropna().unique().tolist()
table_category_names = filtered_df['category_name'].dropna().unique().tolist()

# Layout: 4 columns in one row
col1, col2, col3, col4 = st.columns(4)

with col1:
    selected_months = st.multiselect("Select Month(s)", unique_months, default=unique_months[:1])

with col2:
    selected_table_accounts = st.multiselect("Select Account(s)", table_account_names, default=table_account_names[:1])

with col3:
    selected_transaction_types = st.multiselect("Select Transaction Type(s)", table_transaction_types, default=table_transaction_types[:1])

with col4:
    selected_category_names = st.multiselect("Select Category(ies)", table_category_names, default=table_category_names[:1])

# Filter DataFrame
table_filtered_df = filtered_df[
    filtered_df['month_year_str'].isin(selected_months) &
    filtered_df['account_name'].isin(selected_table_accounts) &
    filtered_df['transaction_type'].isin(selected_transaction_types) &
    filtered_df['category_name'].isin(selected_category_names)
]

# Transactions Table
transaction_table_df = table_filtered_df[
    ['date', 'description', 'sub_description', 'category_name', 'amount', 'account_name', 'transaction_type']
].sort_values(by='date', ascending=False)

# Calculate total amount and append as a new row
total_amount = transaction_table_df['amount'].sum()
total_row = pd.DataFrame({
    'date': [''],
    'description': [''],
    'sub_description': [''],
    'category_name': ['Total'],
    'amount': [total_amount],
    'account_name': [''],
    'transaction_type': ['']
})

transaction_table_df = pd.concat([transaction_table_df, total_row], ignore_index=True)

# Display table
st.dataframe(transaction_table_df, use_container_width=True, hide_index=True)
