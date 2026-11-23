*** Settings ***
Documentation       Source and target tables contain every mapped column.
Resource            ../resources/common.resource
Test Template       Target Schema Should Match Mapping
Test Tags           schema


*** Test Cases ***    MAPPING
Customers Schema      customers
Deposit Accounts Schema    deposit_accounts
Loans Schema          loans
