"""
Tax Wizard - Configuration & Constants
Indian Income Tax Slabs for FY 2025-26 (AY 2026-27)
"""

# === NEW TAX REGIME (Default from FY 2023-24, updated Budget 2024) ===
NEW_REGIME_SLABS = [
    (300000,   0.00),   # 0 - 3L: Nil
    (400000,   0.05),   # 3L - 7L: 5%
    (300000,   0.10),   # 7L - 10L: 10%
    (200000,   0.15),   # 10L - 12L: 15%
    (300000,   0.20),   # 12L - 15L: 20%
    (float('inf'), 0.30),  # 15L+: 30%
]
NEW_REGIME_STANDARD_DEDUCTION = 75000
NEW_REGIME_REBATE_LIMIT = 700000  # Section 87A rebate up to 7L taxable income
NEW_REGIME_REBATE_MAX = 25000

# === OLD TAX REGIME ===
OLD_REGIME_SLABS = [
    (250000,   0.00),   # 0 - 2.5L: Nil
    (250000,   0.05),   # 2.5L - 5L: 5%
    (500000,   0.20),   # 5L - 10L: 20%
    (float('inf'), 0.30),  # 10L+: 30%
]
OLD_REGIME_STANDARD_DEDUCTION = 50000
OLD_REGIME_REBATE_LIMIT = 500000  # Section 87A rebate up to 5L taxable income
OLD_REGIME_REBATE_MAX = 12500

# === DEDUCTION LIMITS (Old Regime) ===
DEDUCTION_LIMITS = {
    "80C": {
        "max": 150000,
        "label": "Section 80C (PPF, ELSS, LIC, EPF, etc.)",
        "description": "Investments in PPF, ELSS mutual funds, life insurance premiums, EPF contribution, NSC, 5-year FD, tuition fees, home loan principal",
    },
    "80D_self": {
        "max": 25000,  # 50000 if senior citizen
        "label": "Section 80D - Self & Family (Health Insurance)",
        "description": "Health insurance premium for self, spouse, and dependent children",
    },
    "80D_parents": {
        "max": 25000,  # 50000 if parents are senior citizens
        "label": "Section 80D - Parents (Health Insurance)",
        "description": "Health insurance premium for parents",
    },
    "80CCD1B": {
        "max": 50000,
        "label": "Section 80CCD(1B) - NPS Additional",
        "description": "Additional deduction for contribution to National Pension System (over and above 80C)",
    },
    "80CCD2": {
        "max": float('inf'),  # 14% of basic for central govt, 10% for others
        "label": "Section 80CCD(2) - Employer NPS Contribution",
        "description": "Employer's contribution to NPS (up to 14% of salary for central govt, 10% for others). Available in BOTH regimes.",
        "both_regimes": True,
    },
    "80E": {
        "max": float('inf'),  # No limit, but only interest component
        "label": "Section 80E - Education Loan Interest",
        "description": "Interest paid on education loan for higher studies (no upper limit, available for 8 years from start of repayment)",
    },
    "80TTA": {
        "max": 10000,
        "label": "Section 80TTA - Savings Account Interest",
        "description": "Interest earned on savings bank accounts",
    },
    "24b": {
        "max": 200000,
        "label": "Section 24(b) - Home Loan Interest",
        "description": "Interest paid on home loan for self-occupied property",
    },
    "HRA": {
        "max": float('inf'),
        "label": "HRA Exemption",
        "description": "House Rent Allowance exemption (calculated based on rent paid, salary, and city)",
    },
}

# === SURCHARGE RATES (applicable on tax amount) ===
SURCHARGE_SLABS = [
    (5000000,   0.00),   # Up to 50L: Nil
    (10000000,  0.10),   # 50L - 1Cr: 10%
    (20000000,  0.15),   # 1Cr - 2Cr: 15%
    (50000000,  0.25),   # 2Cr - 5Cr: 25%
    (float('inf'), 0.25),  # 5Cr+ : 25% (marginal relief may apply)
]

# Health & Education Cess
CESS_RATE = 0.04  # 4% on tax + surcharge

# === COMMON MISSED DEDUCTIONS ===
COMMONLY_MISSED = [
    {
        "section": "80CCD(1B)",
        "tip": "Invest ₹50,000 in NPS for additional tax saving beyond 80C limit",
        "potential_saving_30pct": 15600,
    },
    {
        "section": "80D",
        "tip": "Buy health insurance — ₹25,000 for self/family + ₹25,000-50,000 for parents",
        "potential_saving_30pct": 15600,
    },
    {
        "section": "80E",
        "tip": "Education loan interest is fully deductible with no upper limit",
        "potential_saving_30pct": None,
    },
    {
        "section": "80G",
        "tip": "Donations to eligible charities/funds (50% or 100% deduction)",
        "potential_saving_30pct": None,
    },
    {
        "section": "80TTA",
        "tip": "Savings account interest up to ₹10,000 is deductible",
        "potential_saving_30pct": 3120,
    },
    {
        "section": "24(b)",
        "tip": "Home loan interest up to ₹2L is deductible for self-occupied property",
        "potential_saving_30pct": 62400,
    },
    {
        "section": "HRA",
        "tip": "If you pay rent but don't claim HRA, you're leaving money on the table",
        "potential_saving_30pct": None,
    },
]
