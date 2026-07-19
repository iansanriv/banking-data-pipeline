# Banking Data Pipeline

## A python ETL data pipeline that processes banking data stored in Amazon S3, validates and cleans the data, and loads valid records into Microsoft SQL Server.

## Tools
- Python
- Pandas
- Boto3
- SQLAlchemy
- PyODBC
- Amazon AWS
- Amazon S3
- Microsoft SQL Server

## Pipeline workflow
1. Reads customer, account, and transaction CSV files from an Amazon S3 bucket.
2. Loads the data into Pandas DataFrames.
3. Validates the datasets for:
- Duplicate records
- Invalid customer and account relationships
- Invalid transaction amounts

4.Separates valid and invalid transaction records.

5. Uploads validation output files back to Amazon S3.
6. 
7. Loads validated banking data into Microsoft SQL Server using SQLAlchemy.

## Python packages needed:
- pip install -r requirements.txt
- Requirements
- pandas
- boto3
-SQLAlchemy
-pyodbc

This project is a basic cloud-based banking ETL pipeline using Python, AWS S3, data validation, and SQL Server database integration.
