*** Settings ***
Documentation       Financial totals agree between source and target.
Resource            ../resources/common.resource
Test Template       Column Totals Should Match
Test Tags           aggregates


*** Test Cases ***    MAPPING    SOURCE_COLUMN    TARGET_COLUMN
Deposit Balance Total    deposit_accounts    balance_amt    balance
Loan Principal Total    loans    principal_amt    principal
