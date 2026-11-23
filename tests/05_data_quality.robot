*** Settings ***
Documentation       Mandatory and unique columns in the target.
Resource            ../resources/common.resource
Test Tags           quality


*** Test Cases ***
Mandatory Customer Columns Are Populated
    FOR    ${column}    IN    customer_id    first_name    last_name    status
        Run Keyword And Continue On Failure
        ...    Column Should Not Contain Nulls    target    customer    ${column}
    END

Mandatory Account Columns Are Populated
    FOR    ${column}    IN    account_number    customer_id    balance    currency
        Run Keyword And Continue On Failure
        ...    Column Should Not Contain Nulls    target    deposit_account    ${column}
    END

Business Keys Are Unique
    Column Values Should Be Unique    target    customer    customer_id
    Column Values Should Be Unique    target    deposit_account    account_number
    Column Values Should Be Unique    target    loan    loan_number
    Column Values Should Be Unique    target    customer    email
