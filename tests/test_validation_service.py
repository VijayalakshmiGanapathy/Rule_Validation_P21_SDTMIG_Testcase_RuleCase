import pandas as pd

from app.services.validation_service import ValidationService


def test_build_remarks_success():
    service = ValidationService()

    remarks = service._build_remarks(
        issue_present=True,
        p21_rule_present=True,
        study_present=True,
        test_case_present=True,
        rule_cases_present=True,
        domain_match=True,
    )

    assert remarks == "All validations passed"


def test_build_remarks_failure():
    service = ValidationService()

    remarks = service._build_remarks(
        issue_present=False,
        p21_rule_present=False,
        study_present=False,
        test_case_present=False,
        rule_cases_present=False,
        domain_match=False,
    )

    assert "Domain mismatch" in remarks


def test_check_rule_cases_found():
    service = ValidationService()

    df = pd.DataFrame(
        {
            "Col1": ["SD0001", "SD0002"],
            "Col2": ["SD0003", "SD0004"],
        }
    )

    assert service._check_rule_cases(df, "SD0002") is True


def test_check_rule_cases_not_found():
    service = ValidationService()

    df = pd.DataFrame(
        {
            "Col1": ["SD0001", "SD0002"],
            "Col2": ["SD0003", "SD0004"],
        }
    )

    assert service._check_rule_cases(df, "SD9999") is False