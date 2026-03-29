# 🧙 Tax Wizard — AI-Powered Indian Tax Advisor

> **ET AI Hackathon 2026 | Problem Statement 9: AI Money Mentor**
>
> *95% of Indians don't have a financial plan. Tax Wizard makes tax optimization as easy as filling a form.*

## 🎯 Problem

India has 14 crore+ income tax filers, but most salaried individuals:
- Don't know whether Old or New tax regime is better **for them**
- Miss legitimate deductions worth ₹50,000–₹2,00,000/year in tax savings
- Pay ₹5,000–₹25,000 to CAs for advice that could be automated
- Make tax-saving investment decisions in January–March panic, not strategically

## 💡 Solution

**Tax Wizard** is an AI-powered tax advisor that:

1. **Compares Old vs New Regime** with your exact salary structure and deductions
2. **Identifies Missed Deductions** — sections you're not utilizing, with exact savings potential
3. **Generates Personalized AI Advice** — LLM-powered recommendations for your specific income bracket, age, and financial situation
4. **Visualizes Everything** — interactive charts showing where your money goes

### Key Differentiators
- **Not a calculator — an advisor.** Goes beyond computation to provide actionable, personalized guidance
- **AI-native.** Uses LLM to generate contextual advice considering the user's complete profile
- **Instant.** Results in seconds vs. days waiting for a CA appointment
- **Free.** Democratizes tax advice for the 95% who can't afford ₹25,000/year advisors

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit Frontend                 │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Input    │  │ Comparison   │  │  AI Advisor   │  │
│  │  Forms    │  │ Dashboard    │  │  Interface    │  │
│  └────┬─────┘  └──────┬───────┘  └───────┬───────┘  │
│       │               │                  │           │
├───────┼───────────────┼──────────────────┼───────────┤
│       ▼               ▼                  ▼           │
│  ┌──────────────────────────────────────────────┐    │
│  │              Tax Engine (Python)              │    │
│  │  ┌────────────┐  ┌─────────────────────────┐ │    │
│  │  │ Old Regime  │  │ New Regime Calculator   │ │    │
│  │  │ Calculator  │  │ (Slabs + Rebate + Cess) │ │    │
│  │  └────────────┘  └─────────────────────────┘ │    │
│  │  ┌────────────┐  ┌─────────────────────────┐ │    │
│  │  │ HRA Calc   │  │ Missed Deduction Finder │ │    │
│  │  └────────────┘  └─────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────┐│    │
│  │  │       Regime Comparator & Recommender    ││    │
│  │  └──────────────────────────────────────────┘│    │
│  └──────────────────────┬───────────────────────┘    │
│                         │                            │
│  ┌──────────────────────▼───────────────────────┐    │
│  │           AI Advisor Module                   │    │
│  │  ┌───────────────┐  ┌──────────────────────┐ │    │
│  │  │ Prompt Builder │  │ LLM API Integration │ │    │
│  │  │ (Context-rich  │  │ (Claude / GPT-4o)   │ │    │
│  │  │  tax profile)  │  │                     │ │    │
│  │  └───────────────┘  └──────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────┐│    │
│  │  │    Fallback Rule-Based Advisor           ││    │
│  │  │    (works without API key)               ││    │
│  │  └──────────────────────────────────────────┘│    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │           Config & Tax Rules                  │    │
│  │  FY 2025-26 Slabs │ Deduction Limits │ Cess  │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Visualization | Plotly |
| Tax Engine | Python (custom rule engine) |
| AI Advisor | Anthropic Claude API / OpenAI GPT-4o |
| Deployment | Streamlit Cloud / Docker |

### Agent Design
- **Tax Computation Agent**: Deterministic engine that computes taxes under both regimes with full slab-by-slab breakdown, HRA calculation, and cess/surcharge
- **Deduction Analysis Agent**: Rule-based scanner that identifies gaps between current deductions and available limits
- **AI Advisory Agent**: LLM-powered advisor that synthesizes the user's complete financial profile, tax computation results, and missed deductions into personalized, actionable recommendations
- **Fallback Logic**: Rule-based advisor provides recommendations even without an API key — ensuring the tool works for everyone

## 📈 Impact Model

### Quantifiable Impact

| Metric | Value | Assumptions |
|--------|-------|-------------|
| Target Users | 1 crore salaried taxpayers | 7 crore ITR filers, ~50% salaried, ~30% could benefit |
| Avg Tax Saved per User | ₹15,000–₹50,000/year | Based on missed 80C, 80D, NPS deductions |
| Aggregate Tax Savings | ₹1,500–₹5,000 Cr/year | Conservative: 10L users × ₹15K avg |
| Time Saved per User | 4–8 hours/year | vs. manual research + CA consultation |
| CA Fee Saved | ₹5,000–₹25,000/user | Democratizes advice for non-HNI taxpayers |

### Business Impact for ET
- **User Acquisition**: Free tax tool drives millions of new ET users during Jan–March tax season
- **Data Moat**: Anonymous, aggregated tax behavior data across income brackets
- **Cross-sell**: Natural entry point for ET's financial services marketplace (insurance, mutual funds, NPS)
- **Retention**: Users return annually for updated tax advice → habitual ET usage

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- (Optional) Anthropic or OpenAI API key for AI-powered advice

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/tax-wizard.git
cd tax-wizard

# Install dependencies
pip install -r requirements.txt

# (Optional) Set up API key for AI advisor
cp .env.example .env
# Edit .env and add your API key

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

### Usage
1. Enter your salary details in the sidebar
2. Add your current deductions (80C, 80D, NPS, etc.)
3. View the instant Old vs New regime comparison
4. Check missed deductions section for savings opportunities
5. Click "Get AI Advice" for personalized recommendations

## 📁 Project Structure

```
tax-wizard/
├── app.py              # Main Streamlit application & UI
├── tax_engine.py       # Tax calculation engine (both regimes)
├── ai_advisor.py       # LLM integration for personalized advice
├── config.py           # Tax slabs, deduction limits, constants
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md           # This file
```

## 🛣️ Roadmap (Post-Hackathon)

- [ ] **Form 16 PDF Parser** — Upload Form 16, auto-extract all fields
- [ ] **CAMS/KFintech Integration** — Auto-detect 80C investments from MF statements
- [ ] **Multi-year Comparison** — Track tax optimization progress year-over-year
- [ ] **Vernacular Support** — Hindi, Tamil, Telugu, Bengali interfaces
- [ ] **WhatsApp Bot** — Tax advice via WhatsApp for mass accessibility
- [ ] **Employer Integration** — Plug into HRMS for auto-populated salary structures

## ⚠️ Disclaimer

This tool provides AI-generated guidance for **educational purposes only**. Tax calculations are based on publicly available information about Indian Income Tax Act provisions for FY 2025-26. Always consult a qualified Chartered Accountant (CA) for professional tax advice. The creators are not responsible for any financial decisions made based on this tool's output.

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

*Built with ❤️ for ET AI Hackathon 2026 | Problem Statement 9: AI Money Mentor*
