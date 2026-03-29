"""
Tax Wizard - Form 16 PDF Parser
Extracts salary structure and deduction details from uploaded Form 16 PDF.
Required by PS9: "Upload Form 16 or input salary structure"
"""

import re


def parse_form16(pdf_file) -> dict:
    """
    Parse an uploaded Form 16 PDF and extract key financial fields.

    Returns dict with extracted values, or empty dict if parsing fails.
    Uses pdfplumber for text extraction with regex pattern matching.
    """
    try:
        import pdfplumber
        import io

        extracted = {
            "gross_salary": 0,
            "basic_salary": 0,
            "hra_received": 0,
            "standard_deduction": 0,
            "sec_80c": 0,
            "sec_80d": 0,
            "sec_80ccd1b": 0,
            "sec_80ccd2": 0,
            "sec_80e": 0,
            "sec_80tta": 0,
            "sec_24b": 0,
            "total_income": 0,
            "tax_payable": 0,
            "tds_deducted": 0,
            "parse_success": False,
            "raw_text": "",
            "fields_found": [],
        }

        # Read PDF
        if hasattr(pdf_file, 'read'):
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)
            pdf = pdfplumber.open(io.BytesIO(pdf_bytes))
        else:
            pdf = pdfplumber.open(pdf_file)

        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        pdf.close()
        extracted["raw_text"] = full_text

        if not full_text.strip():
            return extracted

        # Normalize text for pattern matching
        text = full_text.replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "")

        # === Pattern matching for common Form 16 fields ===

        # Gross salary (multiple patterns)
        patterns_gross = [
            r"(?:Gross\s+(?:Total\s+)?Salary|Gross\s+Salary|Total\s+Salary)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"(?:1\s*[\.\)]\s*)?Salary\s+as\s+per\s+.*?17\(1\).*?(\d{5,})",
            r"Gross\s+total\s+income.*?(\d{5,})",
        ]
        for pattern in patterns_gross:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = float(match.group(1))
                if val > 10000:  # Sanity check
                    extracted["gross_salary"] = val
                    extracted["fields_found"].append("Gross Salary")
                    break

        # Standard deduction
        patterns_std = [
            r"(?:Standard\s+[Dd]eduction).*?(\d{5,})",
            r"(?:16\s*[\.\)]?\s*[iI]?\s*[aA]?).*?[Ss]tandard.*?(\d{5,})",
        ]
        for pattern in patterns_std:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = float(match.group(1))
                if 40000 <= val <= 75000:
                    extracted["standard_deduction"] = val
                    extracted["fields_found"].append("Standard Deduction")
                    break

        # Section 80C
        patterns_80c = [
            r"(?:80\s*C\b|Section\s+80C).*?(\d{5,})",
            r"(?:VI[\-\s]*A).*?80C.*?(\d{5,})",
        ]
        for pattern in patterns_80c:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = float(match.group(1))
                if val <= 150000:
                    extracted["sec_80c"] = val
                    extracted["fields_found"].append("Section 80C")
                    break

        # Section 80D
        match_80d = re.search(r"(?:80\s*D\b|Section\s+80D).*?(\d{4,})", text, re.IGNORECASE)
        if match_80d:
            val = float(match_80d.group(1))
            if val <= 100000:
                extracted["sec_80d"] = val
                extracted["fields_found"].append("Section 80D")

        # Section 80CCD(1B) NPS
        match_nps = re.search(r"(?:80\s*CCD.*?1B|NPS).*?(\d{4,})", text, re.IGNORECASE)
        if match_nps:
            val = float(match_nps.group(1))
            if val <= 50000:
                extracted["sec_80ccd1b"] = val
                extracted["fields_found"].append("Section 80CCD(1B)")

        # Section 80CCD(2) Employer NPS
        match_nps2 = re.search(r"(?:80\s*CCD.*?2\b).*?(\d{4,})", text, re.IGNORECASE)
        if match_nps2:
            val = float(match_nps2.group(1))
            extracted["sec_80ccd2"] = val
            extracted["fields_found"].append("Section 80CCD(2)")

        # Home loan interest 24(b)
        match_24b = re.search(r"(?:24\s*[\(\[]?\s*b|[Hh]ome\s+[Ll]oan\s+[Ii]nterest).*?(\d{5,})", text, re.IGNORECASE)
        if match_24b:
            val = float(match_24b.group(1))
            if val <= 200000:
                extracted["sec_24b"] = val
                extracted["fields_found"].append("Section 24(b)")

        # Education loan 80E
        match_80e = re.search(r"(?:80\s*E\b).*?(\d{4,})", text, re.IGNORECASE)
        if match_80e:
            extracted["sec_80e"] = float(match_80e.group(1))
            extracted["fields_found"].append("Section 80E")

        # Total income
        match_total = re.search(r"(?:Total\s+[Ii]ncome|Net\s+[Tt]axable\s+[Ii]ncome).*?(\d{5,})", text, re.IGNORECASE)
        if match_total:
            val = float(match_total.group(1))
            if val > 10000:
                extracted["total_income"] = val
                extracted["fields_found"].append("Total Income")

        # TDS deducted
        match_tds = re.search(r"(?:TDS|[Tt]ax\s+[Dd]educted).*?(\d{4,})", text, re.IGNORECASE)
        if match_tds:
            extracted["tds_deducted"] = float(match_tds.group(1))
            extracted["fields_found"].append("TDS Deducted")

        # Estimate basic salary if not found (typically 40-50% of gross)
        if extracted["gross_salary"] > 0 and extracted["basic_salary"] == 0:
            extracted["basic_salary"] = int(extracted["gross_salary"] * 0.4)

        # Mark success if we found at least gross salary
        if extracted["gross_salary"] > 0 or len(extracted["fields_found"]) >= 2:
            extracted["parse_success"] = True

        return extracted

    except ImportError:
        return {
            "parse_success": False,
            "error": "pdfplumber not installed. Run: pip install pdfplumber",
            "fields_found": [],
        }
    except Exception as e:
        return {
            "parse_success": False,
            "error": str(e),
            "fields_found": [],
        }
