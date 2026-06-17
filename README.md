# P21–SDTMIG Rule Validation Framework

## Overview

The **P21–SDTMIG Rule Validation Framework** is a FastAPI-based automation project designed to validate **Pinnacle 21 (P21) Rule IDs** against master reference files and generate a consolidated validation report.

The framework verifies that each Rule ID configured for a specific **Batch** and **Host Generator Key** exists in:

* P21 **Issue Summary** sheet
* P21 **Rules** sheet
* **SDTMIG Rule Test Case** – Study sheet
* **SDTMIG Rule Test Case** – Test Case sheet
* **SDTMIG Rule Test Case** – Rule Cases sheet

Additionally, it validates that the **Domain** associated with the Rule ID matches the expected domain defined in the **SDTM_P21_Working_Rules_and_15_Batches** master file.

---

# Features

* FastAPI REST API implementation
* Validation of Rule IDs across multiple Excel sources
* Support for validating all 15 batches automatically
* Batch-specific validation using Batch and Host Generator Key
* Automatic forward fill (`ffill`) for grouped domain values in P21 Issue Summary
* Excel report generation with freeze panes
* Structured logging
* Custom exception handling
* Unit testing with pytest
* PEP 8 compliant and modular architecture
* Easy to extend for future validation rules

---

# Project Structure

```
rule_injection_validation_P21_SDTMIG_Testcase_RuleCase/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── main.py
│   └── __init__.py
│
├── data/
│   ├── master/
│   │   ├── SDTM_P21_Working_Rules_and_15_Batches.xlsx
│   │   └── SDTMIG Rule Test Case 1.xlsx
│   │
│   ├── p21_reports/
│   │   ├── pinnacle21-report-B01_DM_dates.xlsx
│   │   ├── pinnacle21-report-B02_*.xlsx
│   │   └── ...
│   │
│   └── output/
│
├── logs/
│
├── tests/
│
├── requirements.txt
└── README.md
```

---

# Input Files

## Master File 1

**SDTM_P21_Working_Rules_and_15_Batches.xlsx**

Sheet used:

* `15 Batches`

Important columns:

* Batch
* Assigned Host Protocol
* Host Generator Key
* Rule ID
* Primitive
* Domain
* Target Variables
* # Protocols Detected
* Total Findings
* Rule Message

---

## Master File 2

**SDTMIG Rule Test Case 1.xlsx**

Sheets used:

* Study
* Test Case
* Rule Cases

---

## P21 Reports

Each batch should have its own P21 validation report.

Examples:

```
pinnacle21-report-B01_DM_dates.xlsx
pinnacle21-report-B02_DM_flags.xlsx
...
```

Sheets used:

* Issue Summary
* Rules

---

# Validation Workflow

For every Rule ID:

1. Read the `15 Batches` sheet.
2. Filter by:

   * Batch
   * Host Generator Key
3. Identify the corresponding P21 report.
4. Read the P21 `Issue Summary` sheet.
5. Apply forward fill (`ffill`) to the `Source` column to populate grouped domain values.
6. Check whether the Rule ID exists in:

   * P21 Issue Summary
   * P21 Rules
   * SDTMIG Study
   * SDTMIG Test Case
   * SDTMIG Rule Cases
7. Compare the expected Domain from the master file with the P21 `Source` domain.
8. Record PASS or FAIL and generate the final validation report.

---

# Output Report

The generated Excel report contains columns such as:

* Batch
* Host Generator Key
* Rule ID
* Expected Domain
* P21 Report File
* P21 Issue Summary Present
* P21 Rules Present
* SDTMIG Study Present
* SDTMIG Test Case Present
* SDTMIG Rule Cases Present
* P21 Domain
* Domain Match
* Final Status
* Remarks

The first row is frozen for easier navigation.

---

# API Endpoint

## POST `/validate`

### Request Body

```json
{
    "batch": "B01_DM_dates",
    "host_generator_key": "oncology_nsclc"
}
```

To validate all available batches:

```json
{
    "batch": null,
    "host_generator_key": null
}
```

---

# Installation

## Create a virtual environment

```bash
python -m venv venv
```

Activate it:

Windows:

```bash
venv\Scripts\activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Application

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```
http://127.0.0.1:8000/openapi.json
```

---

# Running Unit Tests

Execute all tests:

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

Run with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

---

# Logging

Application logs are written to:

```
logs/app.log
```

Logs include:

* Validation start/end
* File loading
* Missing files or sheets
* Validation progress
* Exceptions and errors

---

# Exception Handling

Custom exceptions are used for predictable error handling:

* `FileMissingError`
* `SheetMissingError`
* `ValidationError`

The API returns meaningful HTTP error responses when failures occur.

---

# Coding Standards

This project follows:

* PEP 8 coding conventions
* Modular architecture
* Separation of concerns
* Type hints where appropriate
* Reusable service methods
* Structured logging
* Unit-test-friendly design

---
