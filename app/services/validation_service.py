from pathlib import Path
import pandas as pd

from app.core.config import (
    WORKING_RULES_FILE,
    SDTMIG_FILE,
    P21_REPORT_DIR,
    OUTPUT_DIR,
    WORKING_RULES_SHEET,
    SDTMIG_STUDY_SHEET,
    SDTMIG_TEST_CASE_SHEET,
    SDTMIG_RULE_CASES_SHEET,
    P21_ISSUE_SUMMARY_SHEET,
    P21_RULES_SHEET,
)
from app.core.logging_config import logger
from app.utils.excel_reader import read_excel_sheet, clean_columns
from app.utils.report_writer import write_excel_report


class ValidationService:
    def validate(self, batch: str | None = None, host_generator_key: str | None = None) -> dict:
        logger.info("Validation started")

        master_df = self._load_working_rules(batch, host_generator_key)
        study_df, test_case_df, rule_cases_df = self._load_sdtmig_master()

        results = []

        for _, row in master_df.iterrows():
            batch_name = str(row["Batch"]).strip()
            rule_id = str(row["Rule ID"]).strip()
            expected_domain = str(row["Domain"]).strip()
            host_key = str(row["Host Generator Key"]).strip()

            p21_file = self._find_p21_report(batch_name)

            if p21_file is None:
                results.append(
                    self._build_missing_report_row(row, "P21 report file not found")
                )
                continue

            issue_df, p21_rules_df = self._load_p21_report(p21_file)

            result_row = self._validate_rule(
                row=row,
                rule_id=rule_id,
                expected_domain=expected_domain,
                host_key=host_key,
                p21_file=p21_file,
                issue_df=issue_df,
                p21_rules_df=p21_rules_df,
                study_df=study_df,
                test_case_df=test_case_df,
                rule_cases_df=rule_cases_df,
            )

            results.append(result_row)

        report_df = pd.DataFrame(results)

        output_path = OUTPUT_DIR / "rule_validation_report.xlsx"
        report_file = write_excel_report(report_df, output_path)

        logger.info("Validation completed")

        return {
            "message": "Validation completed successfully",
            "total_rules_validated": len(report_df),
            "output_file": report_file,
        }

    def _load_working_rules(
        self,
        batch: str | None,
        host_generator_key: str | None,
    ) -> pd.DataFrame:
        df = read_excel_sheet(WORKING_RULES_FILE, WORKING_RULES_SHEET)
        df = clean_columns(df)

        required_columns = [
            "Batch",
            "Assigned Host Protocol",
            "Host Generator Key",
            "Rule ID",
            "Primitive",
            "Domain",
            "Target Variables",
            "# Protocols Detected",
            "Total Findings",
            "Rule Message",
        ]

        self._check_required_columns(df, required_columns, WORKING_RULES_SHEET)

        if batch:
            df = df[df["Batch"].astype(str).str.strip() == batch]

        if host_generator_key:
            df = df[df["Host Generator Key"].astype(str).str.strip() == host_generator_key]

        return df

    def _load_sdtmig_master(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        study_df = clean_columns(read_excel_sheet(SDTMIG_FILE, SDTMIG_STUDY_SHEET))
        test_case_df = clean_columns(read_excel_sheet(SDTMIG_FILE, SDTMIG_TEST_CASE_SHEET))
        rule_cases_df = clean_columns(read_excel_sheet(SDTMIG_FILE, SDTMIG_RULE_CASES_SHEET))

        self._check_required_columns(study_df, ["Rule ID", "Domain"], SDTMIG_STUDY_SHEET)
        self._check_required_columns(test_case_df, ["Rule ID", "Domain"], SDTMIG_TEST_CASE_SHEET)

        return study_df, test_case_df, rule_cases_df

    def _find_p21_report(self, batch: str) -> Path | None:
        files = list(P21_REPORT_DIR.glob(f"*{batch}*.xlsx"))

        if not files:
            return None

        return files[0]

    def _load_p21_report(self, p21_file: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        issue_df = clean_columns(
            read_excel_sheet(
                p21_file,
                P21_ISSUE_SUMMARY_SHEET,
                skiprows=3,
            )
        )

        rules_df = clean_columns(read_excel_sheet(p21_file, P21_RULES_SHEET))

        required_issue_columns = [
            "Source",
            "Pinnacle 21 ID",
            "Message",
            "Severity",
            "Found",
        ]

        required_rules_columns = [
            "Pinnacle 21 ID",
            "Publisher ID",
            "Message",
            "Description",
            "Category",
            "Severity",
        ]

        self._check_required_columns(issue_df, required_issue_columns, P21_ISSUE_SUMMARY_SHEET)
        self._check_required_columns(rules_df, required_rules_columns, P21_RULES_SHEET)

        issue_df["Source"] = issue_df["Source"].ffill()

        return issue_df, rules_df

    def _validate_rule(
        self,
        row: pd.Series,
        rule_id: str,
        expected_domain: str,
        host_key: str,
        p21_file: Path,
        issue_df: pd.DataFrame,
        p21_rules_df: pd.DataFrame,
        study_df: pd.DataFrame,
        test_case_df: pd.DataFrame,
        rule_cases_df: pd.DataFrame,
    ) -> dict:
        issue_matches = issue_df[
            issue_df["Pinnacle 21 ID"].astype(str).str.strip() == rule_id
        ]

        p21_rule_present = (
            p21_rules_df["Pinnacle 21 ID"].astype(str).str.strip() == rule_id
        ).any()

        study_present = (
            study_df["Rule ID"].astype(str).str.strip() == rule_id
        ).any()

        test_case_present = (
            test_case_df["Rule ID"].astype(str).str.strip() == rule_id
        ).any()

        rule_cases_present = self._check_rule_cases(rule_cases_df, rule_id)

        issue_present = not issue_matches.empty

        p21_domain = ""
        domain_match = False

        if issue_present:
            p21_domain = ", ".join(
                sorted(issue_matches["Source"].dropna().astype(str).str.strip().unique())
            )

            domain_match = expected_domain in p21_domain.split(", ")

        checks = [
            issue_present,
            p21_rule_present,
            study_present,
            test_case_present,
            rule_cases_present,
            domain_match,
        ]

        final_status = "PASS" if all(checks) else "FAIL"

        remarks = self._build_remarks(
            issue_present,
            p21_rule_present,
            study_present,
            test_case_present,
            rule_cases_present,
            domain_match,
        )

        return {
            "Batch": row["Batch"],
            "Host Generator Key": host_key,
            "Rule ID": rule_id,
            "Expected Domain": expected_domain,
            "P21 Report File": p21_file.name,
            "P21 Issue Summary Present": "YES" if issue_present else "NO",
            "P21 Rules Present": "YES" if p21_rule_present else "NO",
            "SDTMIG Study Present": "YES" if study_present else "NO",
            "SDTMIG Test Case Present": "YES" if test_case_present else "NO",
            "SDTMIG Rule Cases Present": "YES" if rule_cases_present else "NO",
            "P21 Domain": p21_domain,
            "Domain Match": "YES" if domain_match else "NO",
            "Final Status": final_status,
            "Remarks": remarks,
        }

    def _check_rule_cases(self, rule_cases_df: pd.DataFrame, rule_id: str) -> bool:
        for column in rule_cases_df.columns:
            if (
                rule_cases_df[column]
                .astype(str)
                .str.strip()
                .eq(rule_id)
                .any()
            ):
                return True

        return False

    def _build_missing_report_row(self, row: pd.Series, remarks: str) -> dict:
        return {
            "Batch": row["Batch"],
            "Host Generator Key": row["Host Generator Key"],
            "Rule ID": row["Rule ID"],
            "Expected Domain": row["Domain"],
            "P21 Report File": "",
            "P21 Issue Summary Present": "NO",
            "P21 Rules Present": "NO",
            "SDTMIG Study Present": "",
            "SDTMIG Test Case Present": "",
            "SDTMIG Rule Cases Present": "",
            "P21 Domain": "",
            "Domain Match": "NO",
            "Final Status": "FAIL",
            "Remarks": remarks,
        }

    def _build_remarks(
        self,
        issue_present: bool,
        p21_rule_present: bool,
        study_present: bool,
        test_case_present: bool,
        rule_cases_present: bool,
        domain_match: bool,
    ) -> str:
        remarks = []

        if not issue_present:
            remarks.append("Rule ID missing in P21 Issue Summary")

        if not p21_rule_present:
            remarks.append("Rule ID missing in P21 Rules sheet")

        if not study_present:
            remarks.append("Rule ID missing in SDTMIG Study sheet")

        if not test_case_present:
            remarks.append("Rule ID missing in SDTMIG Test Case sheet")

        if not rule_cases_present:
            remarks.append("Rule ID missing in SDTMIG Rule Cases sheet")

        if not domain_match:
            remarks.append("Domain mismatch")

        if not remarks:
            return "All validations passed"

        return "; ".join(remarks)

    def _check_required_columns(
        self,
        df: pd.DataFrame,
        required_columns: list[str],
        sheet_name: str,
    ) -> None:
        missing_columns = [
            column for column in required_columns if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns in sheet '{sheet_name}': {missing_columns}"
            )