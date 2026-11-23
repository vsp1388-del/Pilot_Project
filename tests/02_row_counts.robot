*** Settings ***
Documentation       Source and target row counts match per mapped table.
Resource            ../resources/common.resource
Test Template       Row Counts Should Match
Test Tags           counts


*** Test Cases ***    MAPPING
Customers Row Count    customers
Deposit Accounts Row Count    deposit_accounts
Loans Row Count       loans
