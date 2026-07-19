#Import libraries
import pandas as pd
import boto3
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from io import BytesIO, StringIO

#Connection to database
connection_url = URL.create(
    "mssql+pyodbc",
    query={
        "odbc_connect": (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=JAVXKS\\SQLEXPRESS;"
            "DATABASE=BankingPipelineDB;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    }
)

engine = create_engine(connection_url)

#S3 bucket
BUCKET_NAME = "transactions-banking-data-pipeline"

CUSTOMERS_KEY = "raw/customers/customers.csv"
ACCOUNTS_KEY = "raw/accounts/accounts.csv"
TRANSACTIONS_KEY = "raw/transactions/transactions_20260701.csv"

s3 = boto3.client("s3")

#Defining read and write functions
def read_csv_from_s3(bucket, key):
    """Read CSV files from Amazon S3 Bucket"""
    
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    return pd.read_csv(
        BytesIO(response["Body"].read())
    )

def write_dataframe_to_s3(df, bucket, key):
    """Write a Pandas DataFrame as a CSV File to Amazon S3 Bucket"""

    csv_buffer = StringIO()

    df.to_csv(
        csv_buffer,
        index=False
    )

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=csv_buffer.getvalue(),
        ContentType="text/csv"
    )

print("Reading CSV files from Amazon S3 Bucket.")

customers = read_csv_from_s3(
    BUCKET_NAME,
    CUSTOMERS_KEY
)

accounts = read_csv_from_s3(
    BUCKET_NAME,
    ACCOUNTS_KEY
)

transactions = read_csv_from_s3(
    BUCKET_NAME,
    TRANSACTIONS_KEY
)

print (f"Customers: {len(customers)}")
print (f"Accounts: {len(accounts)}")
print (f"Transactions: {len(transactions)}")

#Check for duplicates
print ("Checking duplicates.")

duplicate_customers = customers[
    customers.duplicated(
        subset=["customer_id"],
        keep=False
    )
]

duplicate_accounts = accounts[
    accounts.duplicated(
        subset=["account_id"],
        keep=False
    )
]

duplicate_transactions = transactions[
    transactions.duplicated(
        subset=["transaction_id"],
        keep=False
    )
]

print(f"Duplicate customers: {len(duplicate_customers)}")
print(f"Duplicate accounts: {len(duplicate_accounts)}")
print(f"Duplicate transactions: {len(duplicate_transactions)}")

#Validation of customers
customers["missing_customer_id"] = (
    customers["customer_id"].isna()
)

customers["duplicate_customer"] = customers.duplicated(
    subset=["customer_id"],
    keep=False
)

customers["created_date"] = pd.to_datetime(
    customers["created_date"],
    errors="coerce"
)

customers["invalid_created_date"] = (
    customers["created_date"].isna()
)

valid_customers = customers[
    (~customers["missing_customer_id"])
    & (~customers["duplicate_customer"])
    & (~customers["invalid_created_date"])
].copy()

customers_to_load = valid_customers[
    [
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "state",
        "created_date"
    ]
]

#Validating accounts
accounts["missing_account_id"] = (
    accounts["account_id"].isna()
)

accounts["duplicate_account"] = accounts.duplicated(
    subset=["account_id"],
    keep=False
)

accounts["open_date"] = pd.to_datetime(
    accounts["open_date"],
    errors="coerce"
)

accounts["invalid_open_date"] = (
    accounts["open_date"].isna()
)

valid_customer_ids = set(valid_customers["customer_id"])

accounts["invalid_customer_id"] = (
    ~accounts["customer_id"].isin(valid_customer_ids)
)

print(
    "Accounts with invalid customer IDs:",
    accounts["invalid_customer_id"].sum()
)

valid_accounts = accounts[
    (~accounts["missing_account_id"])
    & (~accounts["duplicate_account"])
    & (~accounts["invalid_customer_id"])
    & (~accounts["invalid_open_date"])
].copy()

accounts_to_load = valid_accounts[
    [
        "account_id",
        "customer_id",
        "account_type",
        "status",
        "opening_balance",
        "open_date"
    ]
]

#Validating transactions
transactions["missing_transaction_id"] = (
    transactions["transaction_id"].isna()
)

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce"
)

transactions["invalid_date"] = (
    transactions["transaction_date"].isna()
)

print("\nChecking invalid transaction amounts.")

transactions["amount"] = pd.to_numeric(
    transactions["amount"],
    errors="coerce"
)

transactions["invalid_amount"] = (
    transactions["amount"].isna()
    | (transactions["amount"] <= 0)
)

print(
    "Transactions with invalid amounts:",
    transactions["invalid_amount"].sum()
)

valid_account_ids = set(valid_accounts["account_id"])

transactions["invalid_account_id"] = (
    ~transactions["account_id"].isin(valid_account_ids)
)

transactions["duplicate_transaction"] = (
    transactions.duplicated(
        subset=["transaction_id"],
        keep=False
    )
)

#Defining validation errors
def get_validation_error(row):
    errors = []

    if row["duplicate_transaction"]:
        errors.append("Duplicate transaction ID")

    if row["invalid_account_id"]:
        errors.append("Invalid account ID")

    if row ["invalid_amount"]:
        errors.append("Invalid amount")

    if row ["invalid_date"]:
        errors.append("Invalid transaction date")

    if row["missing_transaction_id"]:
        errors.append("Missing transaction ID")

    return "; ".join(errors)

transactions["validation_error"] = transactions.apply(
    get_validation_error,
    axis=1
)

valid_transactions = transactions[
    transactions["validation_error"] == ""
].copy()

invalid_transactions = transactions[
    transactions["validation_error"] != ""
].copy()

#Valid transaction data frame with only the required columns
valid_transactions = valid_transactions[
    [
        "transaction_id",
        "account_id",
        "transaction_date",
        "transaction_type",
        "amount"
    ]
]

print("\nValidation results:")
print(f"Valid transactions: {len(valid_transactions)}")
print(f"Invalid transactions: {len(invalid_transactions)}")

#Validation summary
summary = pd.DataFrame({
    "metric": [
        "Total transactions",
        "Valid transactions",
        "Invalid transactions",
        "Invalid account IDs",
        "Invalid amounts",
        "Duplicate transactions IDs"
    ],
    "count" : [
        len(transactions),
        len(valid_transactions),
        len(invalid_transactions),
        transactions["invalid_account_id"].sum(),
        transactions["invalid_amount"].sum(),
        transactions["duplicate_transaction"].sum()
    ]
})

#Uploading output CSV file to Amazon S3 Bucket
print("\nUploading output files to Amazon S3.")

write_dataframe_to_s3(
    valid_transactions,
    BUCKET_NAME,
    "processed/valid_transactions.csv"
)

write_dataframe_to_s3(
    invalid_transactions,
    BUCKET_NAME,
    "reports/invalid_transactions.csv"
)

write_dataframe_to_s3(
    duplicate_customers,
    BUCKET_NAME,
    "reports/duplicate_customers.csv"
)

write_dataframe_to_s3(
    duplicate_accounts,
    BUCKET_NAME,
    "reports/duplicate_accounts.csv"
)

write_dataframe_to_s3(
    duplicate_transactions,
    BUCKET_NAME,
    "reports/duplicate_transactions.csv"
)

write_dataframe_to_s3(
    summary,
    BUCKET_NAME,
    "reports/validation_summary.csv"
)

#Load the tables into "BankingPipelineDB" database
customers_to_load.to_sql(
    "customers",
    engine,
    schema="dbo",
    if_exists="append",
    index=False
)

accounts_to_load.to_sql(
    "accounts",
    engine,
    schema="dbo",
    if_exists="append",
    index=False
)

valid_transactions.to_sql(
    "transactions",
    engine,
    schema="dbo",
    if_exists="append",
    index=False
)

print("\nValidation completed.")