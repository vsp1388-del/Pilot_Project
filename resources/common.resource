*** Settings ***
Documentation       Shared settings and keywords for all validation suites.
Library             ${CURDIR}/../libraries/DataValidationLibrary.py


*** Variables ***
${RULES_WORKBOOK}       ${CURDIR}/../data/rules/business_rules.xlsx


*** Keywords ***
Open Validation Session
    Connect To Databases

Close Validation Session
    Disconnect From Databases
