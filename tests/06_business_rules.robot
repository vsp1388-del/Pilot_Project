*** Settings ***
Documentation       Rules from the Excel rules workbook; each SQL must return the expected value.
Resource            ../resources/common.resource
Test Tags           rules


*** Test Cases ***
Business Rules Workbook Passes
    ${rules}=    Load Business Rules    ${RULES_WORKBOOK}
    FOR    ${rule}    IN    @{rules}
        Run Keyword And Continue On Failure    Business Rule Should Pass    ${rule}
    END
