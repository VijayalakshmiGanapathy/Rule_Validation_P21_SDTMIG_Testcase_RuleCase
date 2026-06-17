from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

MASTER_DIR = BASE_DIR / "data" / "master"
P21_REPORT_DIR = BASE_DIR / "data" / "p21_reports"
OUTPUT_DIR = BASE_DIR / "data" / "output"
LOG_DIR = BASE_DIR / "logs"

WORKING_RULES_FILE = MASTER_DIR / "SDTM_P21_Working_Rules_and_15_Batches.xlsx"
SDTMIG_FILE = MASTER_DIR / "SDTMIG Rule Test Case 1.xlsx"

WORKING_RULES_SHEET = "15 Batches"
SDTMIG_STUDY_SHEET = "Study"
SDTMIG_TEST_CASE_SHEET = "Test Case"
SDTMIG_RULE_CASES_SHEET = "Rule Cases"

P21_ISSUE_SUMMARY_SHEET = "Issue Summary"
P21_RULES_SHEET = "Rules"