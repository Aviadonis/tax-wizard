"""
Tax Wizard - Investment Recommendations Engine
Suggests tax-saving investments ranked by risk profile and liquidity needs.
Required by PS9: "suggests tax-saving investments ranked by risk profile and liquidity needs"
"""

# Risk profiles
RISK_PROFILES = {
    "Conservative": {
        "description": "Capital preservation, minimal risk tolerance",
        "max_equity_pct": 20,
    },
    "Moderate": {
        "description": "Balanced growth with some risk tolerance",
        "max_equity_pct": 50,
    },
    "Aggressive": {
        "description": "High growth, comfortable with market volatility",
        "max_equity_pct": 80,
    },
}

# Tax-saving instruments database
TAX_INSTRUMENTS = [
    # Section 80C instruments
    {
        "name": "Public Provident Fund (PPF)",
        "section": "80C",
        "max_deduction": 150000,
        "lock_in_years": 15,
        "liquidity": "Low",
        "liquidity_score": 1,
        "risk": "None",
        "risk_score": 0,
        "expected_return": "7.1%",
        "return_pct": 7.1,
        "tax_on_returns": "Exempt (EEE)",
        "best_for": ["Conservative", "Moderate"],
        "description": "Government-backed, guaranteed returns, fully tax-free. 15-year lock-in with partial withdrawal after 7 years.",
    },
    {
        "name": "ELSS Mutual Funds",
        "section": "80C",
        "max_deduction": 150000,
        "lock_in_years": 3,
        "liquidity": "Medium",
        "liquidity_score": 3,
        "risk": "High",
        "risk_score": 4,
        "expected_return": "12-15%",
        "return_pct": 13.0,
        "tax_on_returns": "LTCG >₹1.25L taxed at 12.5%",
        "best_for": ["Moderate", "Aggressive"],
        "description": "Shortest lock-in (3 years) among 80C options. Equity exposure with potential for highest returns.",
    },
    {
        "name": "Employee Provident Fund (EPF)",
        "section": "80C",
        "max_deduction": 150000,
        "lock_in_years": 5,
        "liquidity": "Low",
        "liquidity_score": 1,
        "risk": "None",
        "risk_score": 0,
        "expected_return": "8.25%",
        "return_pct": 8.25,
        "tax_on_returns": "Exempt up to ₹2.5L/yr contribution",
        "best_for": ["Conservative", "Moderate"],
        "description": "If employed, employer match makes this effectively 100% return on the matched portion. Auto-deducted from salary.",
    },
    {
        "name": "National Savings Certificate (NSC)",
        "section": "80C",
        "max_deduction": 150000,
        "lock_in_years": 5,
        "liquidity": "Low",
        "liquidity_score": 1,
        "risk": "None",
        "risk_score": 0,
        "expected_return": "7.7%",
        "return_pct": 7.7,
        "tax_on_returns": "Interest taxable (but reinvested interest qualifies for 80C)",
        "best_for": ["Conservative"],
        "description": "Government-backed, fixed 5-year tenure. Interest is taxable but gets reinvested and qualifies for 80C.",
    },
    {
        "name": "5-Year Tax Saver FD",
        "section": "80C",
        "max_deduction": 150000,
        "lock_in_years": 5,
        "liquidity": "Low",
        "liquidity_score": 1,
        "risk": "None",
        "risk_score": 0,
        "expected_return": "7.0-7.5%",
        "return_pct": 7.25,
        "tax_on_returns": "Interest fully taxable at slab rate",
        "best_for": ["Conservative"],
        "description": "Bank FD with 5-year lock-in. Guaranteed returns but interest is fully taxable.",
    },
    {
        "name": "Life Insurance (Term Plan)",
        "section": "80C",
        "max_deduction": 150000,
        "lock_in_years": 0,
        "liquidity": "N/A",
        "liquidity_score": 0,
        "risk": "N/A",
        "risk_score": 0,
        "expected_return": "N/A (pure protection)",
        "return_pct": 0,
        "tax_on_returns": "Claim exempt under 10(10D)",
        "best_for": ["Conservative", "Moderate", "Aggressive"],
        "description": "Essential protection, not an investment. ₹1Cr cover costs ~₹10-15K/year for a 30-year-old.",
    },
    # Section 80CCD(1B) - NPS
    {
        "name": "National Pension System (NPS) - Tier I",
        "section": "80CCD(1B)",
        "max_deduction": 50000,
        "lock_in_years": 60,
        "liquidity": "Very Low",
        "liquidity_score": 0,
        "risk": "Moderate",
        "risk_score": 2,
        "expected_return": "9-12%",
        "return_pct": 10.5,
        "tax_on_returns": "60% lump sum tax-free, 40% annuity taxable",
        "best_for": ["Conservative", "Moderate"],
        "description": "Extra ₹50K deduction over 80C. Locked till 60 but offers equity + debt mix. Great for retirement planning.",
    },
    # Section 80D - Health Insurance
    {
        "name": "Health Insurance (Self & Family)",
        "section": "80D",
        "max_deduction": 25000,
        "lock_in_years": 0,
        "liquidity": "N/A",
        "liquidity_score": 5,
        "risk": "N/A",
        "risk_score": 0,
        "expected_return": "N/A (protection)",
        "return_pct": 0,
        "tax_on_returns": "N/A",
        "best_for": ["Conservative", "Moderate", "Aggressive"],
        "description": "Essential protection + tax saving. ₹5L cover costs ~₹8-15K/year. ₹25K deduction (₹50K for senior citizens).",
    },
    {
        "name": "Health Insurance (Parents)",
        "section": "80D",
        "max_deduction": 50000,
        "lock_in_years": 0,
        "liquidity": "N/A",
        "liquidity_score": 5,
        "risk": "N/A",
        "risk_score": 0,
        "expected_return": "N/A (protection)",
        "return_pct": 0,
        "tax_on_returns": "N/A",
        "best_for": ["Conservative", "Moderate", "Aggressive"],
        "description": "Additional ₹25-50K deduction for parents' health insurance. Critical as parents age.",
    },
    # Section 24(b) - Home Loan
    {
        "name": "Home Loan Interest",
        "section": "24(b)",
        "max_deduction": 200000,
        "lock_in_years": 0,
        "liquidity": "N/A",
        "liquidity_score": 2,
        "risk": "Low",
        "risk_score": 1,
        "expected_return": "Asset appreciation 5-8%",
        "return_pct": 6.0,
        "tax_on_returns": "LTCG on property taxed at 12.5%",
        "best_for": ["Conservative", "Moderate", "Aggressive"],
        "description": "Up to ₹2L deduction on home loan interest. Builds asset + saves tax. Principal repayment qualifies under 80C.",
    },
]


def get_investment_recommendations(
    deductions: dict,
    gross_salary: float,
    risk_profile: str,
    liquidity_need: str,
    age: int,
) -> list:
    """
    Generate ranked investment recommendations based on user profile.

    Returns list of recommendations sorted by priority score.
    """
    recommendations = []

    # Determine what sections have room
    sec_80c_used = deductions.get("80C", 0)
    sec_80c_gap = max(0, 150000 - sec_80c_used)

    sec_80ccd1b_used = deductions.get("80CCD1B", 0)
    sec_nps_gap = max(0, 50000 - sec_80ccd1b_used)

    sec_80d_self_used = deductions.get("80D_self", 0)
    sec_80d_parents_used = deductions.get("80D_parents", 0)

    sec_24b_used = deductions.get("24b", 0)
    sec_24b_gap = max(0, 200000 - sec_24b_used)

    # Liquidity preference scoring
    liquidity_multiplier = {
        "High": {"Very Low": 0.1, "Low": 0.3, "Medium": 0.8, "High": 1.0, "N/A": 0.7},
        "Medium": {"Very Low": 0.3, "Low": 0.6, "Medium": 1.0, "High": 0.9, "N/A": 0.7},
        "Low": {"Very Low": 0.7, "Low": 1.0, "Medium": 0.9, "High": 0.7, "N/A": 0.7},
    }

    for instrument in TAX_INSTRUMENTS:
        # Check if this section has remaining room
        section = instrument["section"]
        if section == "80C" and sec_80c_gap == 0:
            continue
        if section == "80CCD(1B)" and sec_nps_gap == 0:
            continue
        if section == "80D" and "Self" in instrument["name"] and sec_80d_self_used >= 25000:
            continue
        if section == "80D" and "Parents" in instrument["name"] and sec_80d_parents_used >= 25000:
            continue
        if section == "24(b)" and sec_24b_gap == 0:
            continue

        # Calculate priority score
        score = 0

        # Risk profile match (0-30 points)
        if risk_profile in instrument["best_for"]:
            score += 30
        elif risk_profile == "Moderate":
            score += 15  # Moderate matches most things somewhat
        else:
            score += 5

        # Liquidity match (0-25 points)
        liq = instrument["liquidity"]
        liq_mult = liquidity_multiplier.get(liquidity_need, {}).get(liq, 0.5)
        score += int(liq_mult * 25)

        # Tax saving impact (0-25 points)
        max_ded = instrument["max_deduction"]
        if section == "80C":
            effective_ded = min(max_ded, sec_80c_gap)
        elif section == "80CCD(1B)":
            effective_ded = min(max_ded, sec_nps_gap)
        elif section == "24(b)":
            effective_ded = min(max_ded, sec_24b_gap)
        else:
            effective_ded = max_ded

        tax_saving = effective_ded * 0.312  # approx 30% + cess
        if gross_salary <= 500000:
            tax_saving = effective_ded * 0.052
        elif gross_salary <= 1000000:
            tax_saving = effective_ded * 0.208

        impact_score = min(25, int(tax_saving / 2000))
        score += impact_score

        # Return potential (0-15 points)
        score += min(15, int(instrument["return_pct"] * 1.2))

        # Age-based adjustment
        if age < 30 and instrument["risk_score"] >= 3:
            score += 10  # Young investors benefit from equity
        elif age > 50 and instrument["risk_score"] <= 1:
            score += 10  # Older investors benefit from safety

        # Essential protections always rank high
        if "Insurance" in instrument["name"] or "Health" in instrument["name"]:
            if section == "80D" and (sec_80d_self_used == 0 or sec_80d_parents_used == 0):
                score += 20  # Uninsured = high priority

        recommendations.append({
            **instrument,
            "priority_score": score,
            "effective_deduction": effective_ded,
            "estimated_tax_saving": tax_saving,
        })

    # Sort by priority score descending
    recommendations.sort(key=lambda x: x["priority_score"], reverse=True)

    return recommendations


def get_risk_label_color(risk: str) -> str:
    """Return color code for risk level."""
    return {
        "None": "🟢",
        "Low": "🟡",
        "Moderate": "🟠",
        "High": "🔴",
        "N/A": "⚪",
    }.get(risk, "⚪")


def get_liquidity_label(liquidity: str) -> str:
    """Return emoji for liquidity level."""
    return {
        "Very Low": "🔒",
        "Low": "🔐",
        "Medium": "🔓",
        "High": "✅",
        "N/A": "➖",
    }.get(liquidity, "➖")
