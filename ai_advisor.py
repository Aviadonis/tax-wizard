"""
Tax Wizard - AI-Powered Financial Advisor
Uses LLM to generate personalized tax-saving recommendations.
Supports Anthropic Claude and OpenAI GPT APIs.
"""

import os
import json


def build_tax_prompt(user_profile: dict, old_result: dict, new_result: dict, comparison: dict, missed_deductions: list) -> str:
    """Build a detailed prompt for the LLM with all tax context."""

    missed_text = ""
    if missed_deductions:
        missed_items = []
        for m in missed_deductions:
            missed_items.append(
                f"- {m['section']}: Currently ₹{m['current']:,.0f} / Limit ₹{m['limit']:,.0f} → "
                f"Gap ₹{m['gap']:,.0f} (potential saving: ₹{m.get('potential_saving', 0):,.0f})"
            )
        missed_text = "\n".join(missed_items)
    else:
        missed_text = "No obvious missed deductions — user is well-optimized."

    prompt = f"""You are an expert Indian tax advisor AI. Analyze this taxpayer's profile and provide 
personalized, actionable tax-saving advice for FY 2025-26 (AY 2026-27).

## TAXPAYER PROFILE
- Age: {user_profile.get('age', 'Not specified')}
- Annual Gross Salary: ₹{user_profile.get('gross_salary', 0):,.0f}
- Basic Salary: ₹{user_profile.get('basic_salary', 0):,.0f}
- Other Income: ₹{user_profile.get('other_income', 0):,.0f}
- City: {user_profile.get('city_type', 'Not specified')}
- Rent Paid (Annual): ₹{user_profile.get('rent_paid', 0):,.0f}

## TAX COMPARISON
- Old Regime Tax: ₹{old_result['total_tax']:,.0f} (effective rate: {old_result['effective_rate']:.1f}%)
- New Regime Tax: ₹{new_result['total_tax']:,.0f} (effective rate: {new_result['effective_rate']:.1f}%)
- Recommended: {comparison['recommended']} Regime
- Saving: ₹{comparison['saving']:,.0f}/year

## CURRENT DEDUCTIONS CLAIMED
- 80C: ₹{old_result.get('section_80c', 0):,.0f}
- 80D: ₹{old_result.get('section_80d', 0):,.0f}
- 80CCD(1B) NPS: ₹{old_result.get('section_80ccd1b', 0):,.0f}
- 80CCD(2) Employer NPS: ₹{old_result.get('section_80ccd2', 0):,.0f}
- Home Loan Interest 24(b): ₹{old_result.get('section_24b', 0):,.0f}
- HRA Exemption: ₹{old_result.get('hra_exemption', 0):,.0f}

## MISSED DEDUCTION OPPORTUNITIES
{missed_text}

## INSTRUCTIONS
Provide a response with these sections:
1. **Regime Recommendation** — Which regime to choose and why, with specific numbers
2. **Top 3 Tax-Saving Actions** — Ranked by impact, with exact amounts and instruments
3. **Investment Suggestions** — Specific instruments for each deduction (e.g., which ELSS funds, NPS tier)
4. **Common Mistakes to Avoid** — 2-3 pitfalls specific to their income bracket
5. **Monthly Action Plan** — What to do each month to optimize by year-end

Keep the language simple, confident, and specific to Indian tax law. Use ₹ amounts everywhere.
Add a disclaimer that this is AI-generated guidance and not certified financial advice.
"""
    return prompt


def get_ai_advice_anthropic(prompt: str, api_key: str) -> str:
    """Get advice using Anthropic Claude API."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        return f"Error calling Anthropic API: {str(e)}"


def get_ai_advice_openai(prompt: str, api_key: str) -> str:
    """Get advice using OpenAI GPT API."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert Indian tax and financial planning advisor."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"


def get_ai_advice(user_profile: dict, old_result: dict, new_result: dict, comparison: dict, missed_deductions: list, provider: str = "anthropic", api_key: str = None) -> str:
    """Main function to get AI-powered tax advice."""

    prompt = build_tax_prompt(user_profile, old_result, new_result, comparison, missed_deductions)

    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY") if provider == "anthropic" else os.getenv("OPENAI_API_KEY")

    if not api_key:
        return _generate_fallback_advice(comparison, missed_deductions, old_result, new_result)

    if provider == "anthropic":
        return get_ai_advice_anthropic(prompt, api_key)
    else:
        return get_ai_advice_openai(prompt, api_key)


def _generate_fallback_advice(comparison: dict, missed_deductions: list, old_result: dict, new_result: dict) -> str:
    """Generate rule-based advice when no API key is available."""

    advice_parts = []

    # Regime recommendation
    advice_parts.append("## 🏛️ Regime Recommendation\n")
    if comparison["recommended"] == "Old":
        advice_parts.append(
            f"**Choose the Old Tax Regime.** It saves you **₹{comparison['saving']:,.0f}/year** "
            f"(₹{comparison['saving']/12:,.0f}/month) compared to the New Regime. "
            f"Your deductions are significant enough to make the Old Regime worthwhile.\n"
        )
    elif comparison["recommended"] == "New":
        advice_parts.append(
            f"**Choose the New Tax Regime.** It saves you **₹{comparison['saving']:,.0f}/year** "
            f"(₹{comparison['saving']/12:,.0f}/month). Your current deductions aren't high enough "
            f"to justify the Old Regime.\n"
        )
    else:
        advice_parts.append(
            "**Both regimes give the same result.** Consider the New Regime for simplicity — "
            "fewer compliance requirements and no need to maintain investment proofs.\n"
        )

    # Missed deductions
    if missed_deductions:
        advice_parts.append("## 💡 Tax-Saving Opportunities You're Missing\n")
        total_potential = 0
        for m in missed_deductions:
            saving = m.get('potential_saving', 0)
            total_potential += saving
            advice_parts.append(
                f"**{m['section']}**: {m['tip']}\n"
                f"  → Potential tax saving: ₹{saving:,.0f}/year\n"
            )
        advice_parts.append(f"\n**Total potential additional savings: ₹{total_potential:,.0f}/year**\n")

    # Quick tips based on income
    gross = old_result["gross_income"]
    advice_parts.append("## ⚡ Quick Tips\n")
    if gross > 1500000:
        advice_parts.append("- At your income level, **maxing out all deductions** is critical before choosing Old Regime\n")
        advice_parts.append("- Consider **NPS (80CCD1B)** for the extra ₹50,000 deduction above 80C\n")
        advice_parts.append("- **Salary restructuring** (more basic → more HRA/PF benefits) can further optimize\n")
    elif gross > 1000000:
        advice_parts.append("- You're in the **sweet spot** where Old Regime often wins with proper planning\n")
        advice_parts.append("- **ELSS mutual funds** give 80C benefit + potential market returns\n")
        advice_parts.append("- Don't forget **health insurance (80D)** — it's protection + tax saving\n")
    else:
        advice_parts.append("- At your income level, the **New Regime is often simpler and comparable**\n")
        advice_parts.append("- Focus on **building an emergency fund** before tax-saving investments\n")
        advice_parts.append("- **PPF** is a safe option for 80C with guaranteed returns\n")

    advice_parts.append("\n---\n*⚠️ Disclaimer: This is AI-generated guidance for educational purposes. "
                       "Consult a certified tax professional (CA) for personalized advice.*")

    return "\n".join(advice_parts)
