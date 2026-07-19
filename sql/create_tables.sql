CREATE DATABASE BankingPipelineDB;
GO

- - Use the database
USE BankingPipelineDB;
GO
- -Customers table
CREATE TABLE dbo.customers (
customer_id VARCHAR(20) NOT NULL,
first_name VARCHAR(100) NOT NULL,
last_name VARCHAR(100) NOT NULL,
email VARCHAR(255) NOT NULL,
state CHAR(2) NOT NULL,
created_date DATE NOT NULL,

```
CONSTRAINT PK_customers
    PRIMARY KEY (customer_id)
```

);
GO

- -Accounts table
CREATE TABLE dbo.accounts (
account_id VARCHAR(20) NOT NULL,
customer_id VARCHAR(20) NOT NULL,
account_type VARCHAR(50) NOT NULL,
status VARCHAR(50) NOT NULL,
opening_balance DECIMAL(18, 2) NOT NULL,
open_date DATE NOT NULL,

```
CONSTRAINT PK_accounts
    PRIMARY KEY (account_id),

CONSTRAINT FK_accounts_customers
    FOREIGN KEY (customer_id)
    REFERENCES dbo.customers(customer_id)
```

);
GO

- -Transaction table
CREATE TABLE dbo.transactions (
transaction_id VARCHAR(20) NOT NULL,
account_id VARCHAR(20) NOT NULL,
transaction_date DATE NOT NULL,
transaction_type VARCHAR(50) NOT NULL,
amount DECIMAL(18, 2) NOT NULL,

```
CONSTRAINT PK_transactions
    PRIMARY KEY (transaction_id),

CONSTRAINT FK_transactions_accounts
    FOREIGN KEY (account_id)
    REFERENCES dbo.accounts(account_id),

CONSTRAINT CK_transactions_amount
    CHECK (amount > 0)
```

);
GO