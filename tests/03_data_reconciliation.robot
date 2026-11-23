*** Settings ***
Documentation       Row-by-row, column-by-column comparison by business key.
Resource            ../resources/common.resource
Test Template       Table Data Should Reconcile
Test Tags           reconciliation


*** Test Cases ***    MAPPING
Customers Data Reconciles    customers
Deposit Accounts Data Reconciles    deposit_accounts
Loans Data Reconciles    loans
