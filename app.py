"""
🧙 Tax Wizard — AI-Powered Indian Tax Advisor
ET AI Hackathon 2026 | Problem Statement 9: AI Money Mentor

PS9 Requirements addressed:
  1. Upload Form 16 or input salary structure
  2. AI identifies every deduction you're missing
  3. Models old vs. new tax regime with your specific numbers
  4. Suggests tax-saving investments ranked by risk profile and liquidity needs
"""

import streamlit as st
import plotly.graph_objects as go
from tax_engine import (
    compute_old_regime, compute_new_regime,
    compare_regimes, identify_missed_deductions,
)
from ai_advisor import get_ai_advice
from investments import get_investment_recommendations, get_risk_label_color, get_liquidity_label
from form16_parser import parse_form16


# ──────────────────────────────────────────────
# Page Config & Theme-Safe Styling
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Tax Wizard — AI Money Mentor",
    page_icon="🧙",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }

    /* Theme-safe metric cards — works in both light and dark mode */
    [data-testid="stMetric"] {
        background: rgba(102, 126, 234, 0.08);
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid #667eea;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600 !important;
    }

    /* Saving banner */
    .saving-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 1.25rem 1.5rem; border-radius: 1rem;
        text-align: center; font-size: 1.15rem; margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────
def format_inr(amount):
    if amount >= 10000000:
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


def create_comparison_chart(old_result, new_result):
    categories = ["Gross Income", "Total Deductions", "Taxable Income", "Total Tax", "Take Home"]
    old_values = [old_result["gross_income"], old_result["total_deductions"],
                  old_result["taxable_income"], old_result["total_tax"], old_result["take_home_annual"]]
    new_values = [new_result["gross_income"], new_result["total_deductions"],
                  new_result["taxable_income"], new_result["total_tax"], new_result["take_home_annual"]]
    fig = go.Figure(data=[
        go.Bar(name="Old Regime", x=categories, y=old_values, marker_color="#667eea",
               text=[format_inr(v) for v in old_values], textposition="outside"),
        go.Bar(name="New Regime", x=categories, y=new_values, marker_color="#f6ad55",
               text=[format_inr(v) for v in new_values], textposition="outside"),
    ])
    fig.update_layout(
        barmode="group", title="Old vs New Regime Comparison",
        yaxis_title="Amount (₹)", height=450, font=dict(size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=80), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_tax_breakdown_chart(result, regime_name):
    labels = ["Take Home", "Base Tax", "Cess (4%)", "Surcharge"]
    values = [result["take_home_annual"], result["base_tax"] - result["rebate_87a"],
              result["cess"], result["surcharge"]]
    colors = ["#48bb78", "#667eea", "#f6ad55", "#fc8181"]
    filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    if not filtered:
        return None
    labels, values, colors = zip(*filtered)
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.55, marker_colors=colors,
        textinfo="label+percent", textposition="outside",
    )])
    fig.update_layout(title=f"{regime_name} Regime — Income Split", height=350,
                      margin=dict(t=60, b=20), showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
    return fig


def create_deductions_chart(old_result):
    items = {
        "Standard Ded.": old_result.get("standard_deduction", 0),
        "HRA Exemption": old_result.get("hra_exemption", 0),
        "Section 80C": old_result.get("section_80c", 0),
        "Section 80D": old_result.get("section_80d", 0),
        "NPS 80CCD(1B)": old_result.get("section_80ccd1b", 0),
        "Employer NPS": old_result.get("section_80ccd2", 0),
        "Education Loan": old_result.get("section_80e", 0),
        "Home Loan Int.": old_result.get("section_24b", 0),
        "Savings Int.": old_result.get("section_80tta", 0),
    }
    items = {k: v for k, v in items.items() if v > 0}
    if not items:
        return None
    fig = go.Figure(go.Bar(
        x=list(items.values()), y=list(items.keys()), orientation="h",
        marker_color="#667eea", text=[format_inr(v) for v in items.values()], textposition="outside",
    ))
    fig.update_layout(title="Deductions Breakdown (Old Regime)", xaxis_title="Amount (₹)",
                      height=max(250, len(items) * 45 + 100), margin=dict(l=120, t=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧙 Tax Wizard")
    st.markdown("**FY 2025-26 (AY 2026-27)**")

    # ── Input Mode Toggle ──
    st.markdown("---")
    input_mode = st.radio(
        "How would you like to enter your details?",
        ["📄 Upload Form 16", "⚡ Quick Mode (just salary)", "🔧 Detailed Mode"],
        index=1,
        help="Quick Mode needs only your salary. Detailed Mode lets you fine-tune every deduction.",
    )

    # ── Form 16 Upload ──
    f16_data = {}
    if input_mode == "📄 Upload Form 16":
        uploaded_f16 = st.file_uploader(
            "Upload your Form 16 PDF",
            type=["pdf"],
            help="We'll extract salary, deductions, and TDS details automatically.",
        )
        if uploaded_f16 is not None:
            with st.spinner("Parsing Form 16..."):
                f16_data = parse_form16(uploaded_f16)
            if f16_data.get("parse_success"):
                st.success(f"Extracted {len(f16_data.get('fields_found', []))} fields: {', '.join(f16_data['fields_found'])}")
            else:
                st.warning("Could not extract all fields. Switching to Quick Mode — adjust values below.")
        else:
            st.info("Upload your Form 16 PDF to auto-fill all fields.")

    # ── Core Inputs (always visible) ──
    st.markdown("---")
    st.markdown("### 💼 Your Income")
    default_gross = int(f16_data.get("gross_salary", 0)) or 1200000
    default_basic = int(f16_data.get("basic_salary", 0)) or int(default_gross * 0.4)

    gross_salary = st.number_input("Annual Gross Salary / CTC (₹)", min_value=0, max_value=100000000,
                                   value=default_gross, step=50000)
    user_age = st.number_input("Your Age", min_value=18, max_value=100, value=28)

    # ── Quick Mode: smart defaults ──
    is_detailed = (input_mode == "🔧 Detailed Mode") or f16_data.get("parse_success")

    if is_detailed:
        # Full detailed inputs
        basic_salary = st.number_input("Annual Basic Salary (₹)", min_value=0, max_value=gross_salary,
                                       value=min(default_basic, gross_salary), step=10000,
                                       help="Usually 40-50% of gross. Check payslip.")
        other_income = st.number_input("Other Income (₹)", min_value=0, max_value=100000000,
                                       value=0, step=10000)

        st.markdown("---")
        st.markdown("### 🏠 HRA Details")
        hra_received = st.number_input("Annual HRA Received (₹)", min_value=0, max_value=gross_salary,
                                       value=int(basic_salary * 0.4), step=5000)
        rent_paid = st.number_input("Annual Rent Paid (₹)", min_value=0, max_value=10000000,
                                    value=240000, step=10000)
        is_metro = st.selectbox("City Type", ["Metro (Delhi/Mumbai/Chennai/Kolkata)", "Non-Metro"])

        st.markdown("---")
        st.markdown("### 📋 Deductions")
        sec_80c = st.number_input("80C — PPF, ELSS, LIC, EPF (₹)", min_value=0, max_value=150000,
                                  value=min(int(f16_data.get("sec_80c", 0)) or 150000, 150000), step=10000)
        sec_80d_self = st.number_input("80D — Health: Self & Family (₹)", min_value=0, max_value=100000,
                                       value=int(f16_data.get("sec_80d", 0) // 2) if f16_data.get("sec_80d") else 0, step=5000)
        sec_80d_parents = st.number_input("80D — Health: Parents (₹)", min_value=0, max_value=100000,
                                          value=0, step=5000)
        sec_80ccd1b = st.number_input("80CCD(1B) — NPS Extra (₹)", min_value=0, max_value=50000,
                                      value=int(f16_data.get("sec_80ccd1b", 0)), step=10000)
        sec_80ccd2 = st.number_input("80CCD(2) — Employer NPS (₹)", min_value=0,
                                     max_value=max(1, int(basic_salary * 0.14)),
                                     value=int(f16_data.get("sec_80ccd2", 0)), step=5000)
        sec_24b = st.number_input("24(b) — Home Loan Interest (₹)", min_value=0, max_value=200000,
                                  value=int(f16_data.get("sec_24b", 0)), step=10000)
        sec_80e = st.number_input("80E — Education Loan Interest (₹)", min_value=0, max_value=10000000,
                                  value=int(f16_data.get("sec_80e", 0)), step=10000)
        sec_80tta = st.number_input("80TTA — Savings Interest (₹)", min_value=0, max_value=10000,
                                    value=int(f16_data.get("sec_80tta", 0)), step=1000)
    else:
        # Quick Mode — smart defaults based on salary
        basic_salary = int(gross_salary * 0.4)
        other_income = 0
        hra_received = int(basic_salary * 0.4)
        rent_paid = int(gross_salary * 0.2)  # Assume 20% of salary as rent
        is_metro = "Metro (Delhi/Mumbai/Chennai/Kolkata)"

        # Assume common deduction pattern for salaried
        sec_80c = min(150000, int(gross_salary * 0.12))  # EPF usually covers part
        sec_80d_self = 0
        sec_80d_parents = 0
        sec_80ccd1b = 0
        sec_80ccd2 = 0
        sec_24b = 0
        sec_80e = 0
        sec_80tta = 0

        st.caption("💡 Using smart defaults based on your salary. Switch to Detailed Mode for precision.")

    # ── Investment Profile ──
    st.markdown("---")
    st.markdown("### 📊 Investment Profile")
    risk_profile = st.selectbox("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"], index=1)
    liquidity_need = st.selectbox("Liquidity Need", ["High", "Medium", "Low"], index=1,
                                  help="High = need money access soon")

    # ── AI Settings ──
    st.markdown("---")
    st.markdown("### 🤖 AI Advisor")
    ai_provider = st.selectbox("LLM Provider", ["anthropic", "openai"])
    api_key = st.text_input("API Key (optional)", type="password")


# ──────────────────────────────────────────────
# COMPUTE
# ──────────────────────────────────────────────
deductions = {
    "80C": sec_80c, "80D_self": sec_80d_self, "80D_parents": sec_80d_parents,
    "80CCD1B": sec_80ccd1b, "80CCD2": sec_80ccd2, "80E": sec_80e,
    "80TTA": sec_80tta, "24b": sec_24b,
}

old_result = compute_old_regime(gross_salary, basic_salary, hra_received, rent_paid,
                                "Metro" in is_metro, deductions, other_income)
new_result = compute_new_regime(gross_salary, deductions, other_income)
comparison = compare_regimes(old_result, new_result)
missed = identify_missed_deductions(deductions, gross_salary)


# ──────────────────────────────────────────────
# DISPLAY
# ──────────────────────────────────────────────
st.markdown("# 🧙 Tax Wizard")
st.markdown("##### AI-Powered Indian Tax Advisor • FY 2025-26 (AY 2026-27)")
st.markdown("---")

if f16_data.get("parse_success"):
    st.info(f"📄 **Form 16 loaded** — Extracted: {', '.join(f16_data['fields_found'])}. Adjust values in sidebar if needed.")

# Banner
winner_emoji = "📜" if comparison["recommended"] == "Old" else "✨" if comparison["recommended"] == "New" else "⚖️"
st.markdown(f'<div class="saving-banner">{winner_emoji} <strong>{comparison["reason"]}</strong></div>',
            unsafe_allow_html=True)

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Old Regime Tax", format_inr(old_result["total_tax"]),
              delta=f"{old_result['effective_rate']:.1f}% effective", delta_color="off")
with col2:
    st.metric("New Regime Tax", format_inr(new_result["total_tax"]),
              delta=f"{new_result['effective_rate']:.1f}% effective", delta_color="off")
with col3:
    st.metric("You Save", format_inr(comparison["saving"]),
              delta=f"with {comparison['recommended']} Regime", delta_color="off")
with col4:
    best = old_result if comparison["recommended"] == "Old" else new_result
    st.metric("Take-Home/Month", format_inr(best["take_home_monthly"]),
              delta=f"₹{best['take_home_annual']:,.0f}/year", delta_color="off")

st.markdown("---")

# Chart
st.plotly_chart(create_comparison_chart(old_result, new_result), use_container_width=True)

# Tabs
st.markdown("## 📊 Detailed Breakdown")
tab1, tab2, tab3 = st.tabs(["🏛️ Old Regime", "✨ New Regime", "📋 Deductions"])

with tab1:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### Old Regime — Step by Step")
        st.markdown(f"Gross Income: **{format_inr(old_result['gross_income'])}**")
        st.markdown(f"(-) Standard Deduction: {format_inr(old_result['standard_deduction'])}")
        st.markdown(f"(-) HRA Exemption: {format_inr(old_result['hra_exemption'])}")
        st.markdown(f"(-) Section 80C: {format_inr(old_result['section_80c'])}")
        st.markdown(f"(-) Section 80D: {format_inr(old_result['section_80d'])}")
        st.markdown(f"(-) NPS 80CCD(1B): {format_inr(old_result['section_80ccd1b'])}")
        st.markdown(f"(-) Home Loan 24(b): {format_inr(old_result['section_24b'])}")
        st.markdown(f"(-) Other: {format_inr(old_result['section_80e'] + old_result['section_80tta'] + old_result['section_80ccd2'])}")
        st.markdown(f"**Total Deductions: {format_inr(old_result['total_deductions'])}**")
        st.divider()
        st.markdown(f"**Taxable Income: {format_inr(old_result['taxable_income'])}**")
        st.markdown(f"Base Tax: {format_inr(old_result['base_tax'])} | Rebate: {format_inr(old_result['rebate_87a'])} | Cess: {format_inr(old_result['cess'])}")
        st.markdown(f"### Total Tax: {format_inr(old_result['total_tax'])}")
    with c2:
        chart = create_tax_breakdown_chart(old_result, "Old")
        if chart:
            st.plotly_chart(chart, use_container_width=True)

with tab2:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### New Regime — Step by Step")
        st.markdown(f"Gross Income: **{format_inr(new_result['gross_income'])}**")
        st.markdown(f"(-) Standard Deduction: {format_inr(new_result['standard_deduction'])}")
        st.markdown(f"(-) Employer NPS: {format_inr(new_result['section_80ccd2'])}")
        st.markdown(f"**Total Deductions: {format_inr(new_result['total_deductions'])}**")
        st.divider()
        st.markdown(f"**Taxable Income: {format_inr(new_result['taxable_income'])}**")
        st.markdown(f"Base Tax: {format_inr(new_result['base_tax'])} | Rebate: {format_inr(new_result['rebate_87a'])} | Cess: {format_inr(new_result['cess'])}")
        st.markdown(f"### Total Tax: {format_inr(new_result['total_tax'])}")
    with c2:
        chart = create_tax_breakdown_chart(new_result, "New")
        if chart:
            st.plotly_chart(chart, use_container_width=True)

with tab3:
    chart = create_deductions_chart(old_result)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("No deductions entered yet.")

# Missed deductions
if missed:
    st.markdown("---")
    st.markdown("## 💡 Deductions You're Missing")
    total_potential = 0
    for m in missed:
        saving = m.get("potential_saving", 0)
        total_potential += saving
        with st.expander(f"**{m['section']}** — Save up to {format_inr(saving)}/year"):
            st.markdown(f"**Current:** {format_inr(m['current'])} / **Limit:** {format_inr(m['limit'])} / **Gap:** {format_inr(m['gap'])}")
            st.info(m["tip"])
    if total_potential > 0:
        st.success(f"💰 **Total potential savings: {format_inr(total_potential)}/year ({format_inr(total_potential / 12)}/month)**")


# ──────────────────────────────────────────────
# INVESTMENT RECOMMENDATIONS (PS9 Requirement)
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📈 Investment Recommendations")
st.markdown(f"Ranked for your profile: **{risk_profile}** risk · **{liquidity_need}** liquidity · Age **{user_age}**")

recommendations = get_investment_recommendations(deductions, gross_salary, risk_profile, liquidity_need, user_age)

if recommendations:
    for i, rec in enumerate(recommendations[:8]):
        risk_icon = get_risk_label_color(rec["risk"])
        liq_icon = get_liquidity_label(rec["liquidity"])

        with st.expander(
            f"{'🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else f'#{i+1}'} "
            f"**{rec['name']}** — Save {format_inr(rec['estimated_tax_saving'])}/yr "
            f"| {risk_icon} {rec['risk']} | {liq_icon} {rec['liquidity']} liquidity",
            expanded=(i < 3),
        ):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Section", rec["section"])
            with c2:
                st.metric("Return", rec["expected_return"])
            with c3:
                lock = f"{rec['lock_in_years']} yrs" if rec["lock_in_years"] > 0 else "None"
                st.metric("Lock-in", lock)
            with c4:
                st.metric("Tax Saving", format_inr(rec["estimated_tax_saving"]))
            st.markdown(rec["description"])
            st.caption(f"Match score: {rec['priority_score']}/100 · Max deduction: {format_inr(rec['max_deduction'])}")
else:
    st.success("You've maxed out all available deductions!")


# ──────────────────────────────────────────────
# AI ADVISOR
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🤖 AI Tax Advisor")
st.markdown("Get personalized AI-powered recommendations based on your complete profile.")

if st.button("🔮 Get AI Advice", type="primary", use_container_width=True):
    user_profile = {
        "age": user_age, "gross_salary": gross_salary, "basic_salary": basic_salary,
        "other_income": other_income, "city_type": is_metro, "rent_paid": rent_paid,
        "risk_profile": risk_profile, "liquidity_need": liquidity_need,
    }
    with st.spinner("🧙 Analyzing your profile..."):
        advice = get_ai_advice(user_profile, old_result, new_result, comparison, missed,
                               provider=ai_provider, api_key=api_key if api_key else None)
    st.markdown(advice)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; opacity: 0.6; font-size: 0.85rem;'>"
    "🧙 Tax Wizard — ET AI Hackathon 2026 | PS9: AI Money Mentor<br>"
    "⚠️ Educational purposes only. Consult a CA for professional advice."
    "</div>", unsafe_allow_html=True,
)
