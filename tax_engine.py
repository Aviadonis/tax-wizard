"""
Tax Wizard - Tax Calculation Engine
Handles computation for both Old and New Indian tax regimes.
"""

from config import (
    NEW_REGIME_SLABS, NEW_REGIME_STANDARD_DEDUCTION,
    NEW_REGIME_REBATE_LIMIT, NEW_REGIME_REBATE_MAX,
    OLD_REGIME_SLABS, OLD_REGIME_STANDARD_DEDUCTION,
    OLD_REGIME_REBATE_LIMIT, OLD_REGIME_REBATE_MAX,
    CESS_RATE, SURCHARGE_SLABS,
)


def calculate_slab_tax(taxable_income: float, slabs: list) -> tuple[float, list]:
    """Calculate tax based on income slabs. Returns (total_tax, slab_breakdown)."""
    remaining = taxable_income
    total_tax = 0
    breakdown = []

    for slab_limit, rate in slabs:
        if remaining <= 0:
            break
        taxable_in_slab = min(remaining, slab_limit)
        tax_in_slab = taxable_in_slab * rate
        total_tax += tax_in_slab
        if taxable_in_slab > 0:
            breakdown.append({
                "slab_limit": slab_limit,
                "rate": rate,
                "taxable_amount": taxable_in_slab,
                "tax": tax_in_slab,
            })
        remaining -= taxable_in_slab

    return total_tax, breakdown


def calculate_surcharge(tax: float, total_income: float) -> float:
    """Calculate surcharge based on total income."""
    for limit, rate in SURCHARGE_SLABS:
        if total_income <= limit:
            return tax * rate
    return tax * SURCHARGE_SLABS[-1][1]


def calculate_hra_exemption(basic: float, hra_received: float, rent_paid: float, is_metro: bool) -> float:
    """
    Calculate HRA exemption — minimum of:
    1. Actual HRA received
    2. Rent paid - 10% of basic salary
    3. 50% of basic (metro) or 40% of basic (non-metro)
    """
    if rent_paid == 0 or hra_received == 0:
        return 0

    metro_pct = 0.50 if is_metro else 0.40
    exemption = min(
        hra_received,
        max(0, rent_paid - 0.10 * basic),
        metro_pct * basic,
    )
    return max(0, exemption)


def compute_old_regime(
    gross_salary: float,
    basic_salary: float,
    hra_received: float,
    rent_paid: float,
    is_metro: bool,
    deductions: dict,
    other_income: float = 0,
) -> dict:
    """Compute tax under Old Regime with all deductions."""

    # Standard deduction
    std_deduction = min(OLD_REGIME_STANDARD_DEDUCTION, gross_salary)

    # HRA exemption
    hra_exemption = calculate_hra_exemption(basic_salary, hra_received, rent_paid, is_metro)

    # Section-wise deductions
    sec_80c = min(deductions.get("80C", 0), 150000)
    sec_80d_self = min(deductions.get("80D_self", 0), deductions.get("80D_self_limit", 25000))
    sec_80d_parents = min(deductions.get("80D_parents", 0), deductions.get("80D_parents_limit", 25000))
    sec_80ccd1b = min(deductions.get("80CCD1B", 0), 50000)
    sec_80ccd2 = deductions.get("80CCD2", 0)
    sec_80e = deductions.get("80E", 0)
    sec_80tta = min(deductions.get("80TTA", 0), 10000)
    sec_24b = min(deductions.get("24b", 0), 200000)

    total_deductions = (
        std_deduction + hra_exemption +
        sec_80c + sec_80d_self + sec_80d_parents +
        sec_80ccd1b + sec_80ccd2 + sec_80e + sec_80tta + sec_24b
    )

    total_income = gross_salary + other_income
    taxable_income = max(0, total_income - total_deductions)

    # Calculate tax
    base_tax, slab_breakdown = calculate_slab_tax(taxable_income, OLD_REGIME_SLABS)

    # Apply Section 87A rebate
    rebate = 0
    if taxable_income <= OLD_REGIME_REBATE_LIMIT:
        rebate = min(base_tax, OLD_REGIME_REBATE_MAX)

    tax_after_rebate = base_tax - rebate

    # Surcharge
    surcharge = calculate_surcharge(tax_after_rebate, total_income)

    # Cess
    cess = (tax_after_rebate + surcharge) * CESS_RATE

    total_tax = tax_after_rebate + surcharge + cess

    return {
        "regime": "Old",
        "gross_income": total_income,
        "standard_deduction": std_deduction,
        "hra_exemption": hra_exemption,
        "section_80c": sec_80c,
        "section_80d": sec_80d_self + sec_80d_parents,
        "section_80ccd1b": sec_80ccd1b,
        "section_80ccd2": sec_80ccd2,
        "section_80e": sec_80e,
        "section_80tta": sec_80tta,
        "section_24b": sec_24b,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "base_tax": base_tax,
        "rebate_87a": rebate,
        "surcharge": surcharge,
        "cess": cess,
        "total_tax": total_tax,
        "effective_rate": (total_tax / total_income * 100) if total_income > 0 else 0,
        "take_home_annual": total_income - total_tax,
        "take_home_monthly": (total_income - total_tax) / 12,
        "slab_breakdown": slab_breakdown,
    }


def compute_new_regime(
    gross_salary: float,
    deductions: dict,
    other_income: float = 0,
) -> dict:
    """Compute tax under New Regime (limited deductions)."""

    # Only standard deduction and 80CCD(2) allowed
    std_deduction = min(NEW_REGIME_STANDARD_DEDUCTION, gross_salary)
    sec_80ccd2 = deductions.get("80CCD2", 0)  # Employer NPS — allowed in both

    total_deductions = std_deduction + sec_80ccd2
    total_income = gross_salary + other_income
    taxable_income = max(0, total_income - total_deductions)

    # Calculate tax
    base_tax, slab_breakdown = calculate_slab_tax(taxable_income, NEW_REGIME_SLABS)

    # Apply Section 87A rebate
    rebate = 0
    if taxable_income <= NEW_REGIME_REBATE_LIMIT:
        rebate = min(base_tax, NEW_REGIME_REBATE_MAX)

    tax_after_rebate = base_tax - rebate

    # Surcharge
    surcharge = calculate_surcharge(tax_after_rebate, total_income)

    # Cess
    cess = (tax_after_rebate + surcharge) * CESS_RATE

    total_tax = tax_after_rebate + surcharge + cess

    return {
        "regime": "New",
        "gross_income": total_income,
        "standard_deduction": std_deduction,
        "section_80ccd2": sec_80ccd2,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "base_tax": base_tax,
        "rebate_87a": rebate,
        "surcharge": surcharge,
        "cess": cess,
        "total_tax": total_tax,
        "effective_rate": (total_tax / total_income * 100) if total_income > 0 else 0,
        "take_home_annual": total_income - total_tax,
        "take_home_monthly": (total_income - total_tax) / 12,
        "slab_breakdown": slab_breakdown,
    }


def compare_regimes(old_result: dict, new_result: dict) -> dict:
    """Compare both regimes and return recommendation."""
    old_tax = old_result["total_tax"]
    new_tax = new_result["total_tax"]
    saving = abs(old_tax - new_tax)

    if old_tax < new_tax:
        recommended = "Old"
        reason = f"Old Regime saves you ₹{saving:,.0f} per year (₹{saving/12:,.0f}/month)"
    elif new_tax < old_tax:
        recommended = "New"
        reason = f"New Regime saves you ₹{saving:,.0f} per year (₹{saving/12:,.0f}/month)"
    else:
        recommended = "Either"
        reason = "Both regimes result in the same tax. New Regime is simpler with fewer compliance requirements."

    return {
        "recommended": recommended,
        "reason": reason,
        "saving": saving,
        "old_tax": old_tax,
        "new_tax": new_tax,
    }


def identify_missed_deductions(deductions: dict, gross_salary: float) -> list:
    """Identify deductions the user might be missing."""
    missed = []

    if deductions.get("80C", 0) < 150000:
        gap = 150000 - deductions.get("80C", 0)
        missed.append({
            "section": "80C",
            "current": deductions.get("80C", 0),
            "limit": 150000,
            "gap": gap,
            "potential_saving": gap * 0.312,  # 30% + cess approx
            "tip": f"You can invest ₹{gap:,.0f} more in PPF, ELSS, or NPS Tier-I to max out 80C",
        })

    if deductions.get("80CCD1B", 0) == 0:
        missed.append({
            "section": "80CCD(1B)",
            "current": 0,
            "limit": 50000,
            "gap": 50000,
            "potential_saving": 50000 * 0.312,
            "tip": "Invest ₹50,000 in NPS for an additional deduction beyond 80C",
        })

    if deductions.get("80D_self", 0) == 0:
        missed.append({
            "section": "80D (Self)",
            "current": 0,
            "limit": 25000,
            "gap": 25000,
            "potential_saving": 25000 * 0.312,
            "tip": "Get health insurance for self/family — ₹25,000 deduction + actual coverage",
        })

    if deductions.get("80D_parents", 0) == 0:
        missed.append({
            "section": "80D (Parents)",
            "current": 0,
            "limit": 25000,
            "gap": 25000,
            "potential_saving": 25000 * 0.312,
            "tip": "Pay health insurance for parents — additional ₹25,000-₹50,000 deduction",
        })

    if deductions.get("80TTA", 0) == 0:
        missed.append({
            "section": "80TTA",
            "current": 0,
            "limit": 10000,
            "gap": 10000,
            "potential_saving": 10000 * 0.312,
            "tip": "Savings account interest up to ₹10,000 is deductible — check your bank statements",
        })

    if deductions.get("24b", 0) == 0 and gross_salary > 1000000:
        missed.append({
            "section": "24(b)",
            "current": 0,
            "limit": 200000,
            "gap": 200000,
            "potential_saving": 200000 * 0.312,
            "tip": "If you have a home loan, interest up to ₹2L is deductible",
        })

    return missed
