USE BankingPipelineDB;
GO

--Visualize all customers
SELECT *
FROM dbo.customers;
GO

--Visualize all accounts
SELECT *
FROM dbo.accounts;
GO

--Visualize all valid transactions
SELECT *
FROM dbo.transactions
ORDER BY transaction_date DESC;
GO


--Accounts belong to each customer
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    a.account_id,
    a.account_type,
    a.status,
    a.opening_balance
FROM dbo.customers c
INNER JOIN dbo.accounts a
    ON c.customer_id = a.customer_id
ORDER BY c.customer_id;
GO

--Transaction details
-- Joins customers, accounts, and transactions
SELECT
    t.transaction_id,
    t.transaction_date,
    c.customer_id,
    c.first_name,
    c.last_name,
    a.account_id,
    a.account_type,
    t.transaction_type,
    t.amount
FROM dbo.transactions t
INNER JOIN dbo.accounts a
    ON t.account_id = a.account_id
INNER JOIN dbo.customers c
    ON a.customer_id = c.customer_id
ORDER BY t.transaction_date DESC;
GO

--Total transaction amount by account
SELECT
    a.account_id,
    a.account_type,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(t.amount) AS total_transaction_amount
FROM dbo.accounts a
LEFT JOIN dbo.transactions t
    ON a.account_id = t.account_id
GROUP BY
    a.account_id,
    a.account_type
ORDER BY total_transaction_amount DESC;
GO

--Total transaction amount by customer
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(t.amount) AS total_transaction_amount
FROM dbo.customers c
LEFT JOIN dbo.accounts a
    ON c.customer_id = a.customer_id
LEFT JOIN dbo.transactions t
    ON a.account_id = t.account_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name
ORDER BY total_transaction_amount DESC;
GO


--Transaction summary by transaction type
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS average_amount,
    MIN(amount) AS minimum_amount,
    MAX(amount) AS maximum_amount
FROM dbo.transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;
GO


--Accounts with no transactions
SELECT
    a.account_id,
    a.customer_id,
    a.account_type,
    a.status
FROM dbo.accounts a
LEFT JOIN dbo.transactions t
    ON a.account_id = t.account_id
WHERE t.transaction_id IS NULL;
GO

--Customer account summary
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(DISTINCT a.account_id) AS number_of_accounts,
    SUM(a.opening_balance) AS total_opening_balance
FROM dbo.customers c
LEFT JOIN dbo.accounts a
    ON c.customer_id = a.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name
ORDER BY total_opening_balance DESC;
GO