#!/usr/bin/env python3
"""
Bangladesh individual income-tax calculator (deterministic, standard library only).

Scope: PERSONAL / individual income tax under the Income Tax Act 2023 as amended by
the annual Finance Act. Supports Assessment Year (AY) 2026-27 (primary) and AY 2025-26,
plus the four further years the Finance Act 2026 legislated in advance (AY 2027-28 to
AY 2030-31, forward-looking estimates until each year's own Finance Act).

All rates/thresholds live in PARAMS below so a yearly update touches one place.
This module performs NO network calls. It is the single source of arithmetic for the
bd-income-tax skill: the model must never hand-calculate tax.

Usage:
    from tax_calc import compute_tax
    result = compute_tax("2026-27", "general", salary_income=1_260_000)

CLI:
    python3 tax_calc.py --year 2026-27 --category general --salary 800000
    python3 tax_calc.py --selftest      # run the canonical test cases
"""

from __future__ import annotations

import argparse
import copy
import datetime as _dt
import json
from typing import Optional

# ---------------------------------------------------------------------------
# Year parameters. Each figure is sourced in references/sources.md.
# Slab "bands" are the widths/rates that apply to income ABOVE the taxpayer's
# tax-free threshold, in order. (The first 0% band of the published schedule is
# represented by the category threshold itself.)
# ---------------------------------------------------------------------------

# Bands shared by AY 2026-27 to AY 2030-31 up to the 25% slab. [FA-2026] Sch. 2 Part 1.
_BANDS_FA2026_COMMON = [
    (300_000, 0.10),
    (400_000, 0.15),
    (500_000, 0.20),
    (2_000_000, 0.25),
]

PARAMS = {
    "2026-27": {
        "governing_law": (
            "Income Tax Act 2023 as amended by the Finance Act 2026 (Act No. 96 of 2026, "
            "gazetted 30 Jun 2026); rates per its Schedule 2, Part 1, para Ka."
        ),
        "status": "enacted",
        "thresholds": {
            "general": 400_000,
            "female": 450_000,
            "senior": 450_000,            # 65 years or older
            "disabled": 525_000,
            "third_gender": 525_000,
            "freedom_fighter": 550_000,   # gazetted war-wounded freedom fighters
            "july_warrior": 550_000,      # gazetted injured "July fighters" (2024 uprising)
        },
        "disabled_child_extra": 50_000,   # per disabled child/dependant; one parent only
        "bands": _BANDS_FA2026_COMMON + [(None, 0.30)],
        "salary_exemption_cap": 500_000,
        "min_tax": {
            # Flat, location-independent.
            "default": 5_000,
            "new_taxpayer": 1_000,
        },
        "min_tax_area_based": False,
        # Section 78 rebate = lowest of the three candidates.
        "rebate": {"income_rate": 0.03, "investment_rate": 0.10, "cap": 750_000},
        # Return timing: quarterly windows (Sec 170/174). No "Tax Day" cliff.
        "timing_rule": "windows",
        # Flat-rate income (Seventh Schedule): taxed outside the slab schedule.
        "dividend_rate": 0.15,
        "precious_metal_gain_rate": 0.05,
        # Turnover tax on business/profession gross receipts (Sec 163(6)).
        "turnover": {"rule": "sec163_6", "default_rate": 0.01},
    },
    "2025-26": {
        "governing_law": "Income Tax Act 2023 as amended by the Finance Ordinance 2025.",
        "status": "enacted",
        "thresholds": {
            "general": 350_000,
            "female": 400_000,
            "senior": 400_000,
            "disabled": 475_000,
            "third_gender": 475_000,
            "freedom_fighter": 500_000,   # gazetted war-wounded freedom fighters
        },
        "disabled_child_extra": 50_000,
        "bands": [
            (100_000, 0.05),
            (400_000, 0.10),
            (500_000, 0.15),
            (500_000, 0.20),
            (2_000_000, 0.25),
            (None, 0.30),
        ],
        "salary_exemption_cap": 450_000,
        "min_tax": {
            # Area-based (last year of this system).
            "dhaka_ctg_cc": 5_000,   # Dhaka North/South + Chattogram City Corporation
            "other_cc": 4_000,       # other city corporations
            "other": 3_000,          # outside city corporations
            "new_taxpayer": 1_000,
        },
        "min_tax_area_based": True,
        "rebate": {"income_rate": 0.03, "investment_rate": 0.15, "cap": 1_000_000},
        # Return timing: filing after Tax Day forfeits the investment rebate.
        "timing_rule": "tax_day",
        "dividend_rate": None,             # dividends taxed at slab rates this year
        "precious_metal_gain_rate": None,  # not a capital asset before AY 2026-27
        # Legacy gross-receipts floor carried from earlier releases; not re-verified
        # against the AY 2025-26 text (see references/ay-2025-26.md).
        "turnover": {"rule": "legacy_floor", "floor": 40_000_000, "rate": 0.0025},
    },
}


def _forward_year(base: str, law_note: str, **overrides) -> dict:
    p = copy.deepcopy(PARAMS[base])
    p["status"] = "legislated-forward"
    p["governing_law"] = law_note
    p.update(overrides)
    return p


_FORWARD_NOTE = (
    "Income Tax Act 2023 as amended. Rates for AY {ay} were legislated in advance by the "
    "Finance Act 2026 (Schedule 2, Part 1, para {para}) and remain subject to amendment by "
    "a later Finance Act, so treat this as the best current estimate, not a final filing "
    "figure."
)

# AY 2027-28 shares para Ka with AY 2026-27 (identical rates and thresholds).
PARAMS["2027-28"] = _forward_year("2026-27", _FORWARD_NOTE.format(ay="2027-28", para="Ka"))

# AY 2028-29 and 2029-30 (para Kha): higher thresholds, new 35% top band.
PARAMS["2028-29"] = _forward_year(
    "2026-27", _FORWARD_NOTE.format(ay="2028-29", para="Kha"),
    thresholds={
        "general": 450_000, "female": 500_000, "senior": 500_000,
        "disabled": 575_000, "third_gender": 575_000,
        "freedom_fighter": 600_000, "july_warrior": 600_000,
    },
    bands=_BANDS_FA2026_COMMON + [(26_350_000, 0.30), (None, 0.35)],
)
PARAMS["2029-30"] = _forward_year("2028-29", _FORWARD_NOTE.format(ay="2029-30", para="Kha"))

# AY 2030-31 (para Ga).
PARAMS["2030-31"] = _forward_year(
    "2026-27", _FORWARD_NOTE.format(ay="2030-31", para="Ga"),
    thresholds={
        "general": 500_000, "female": 550_000, "senior": 550_000,
        "disabled": 625_000, "third_gender": 625_000,
        "freedom_fighter": 650_000, "july_warrior": 650_000,
    },
    bands=_BANDS_FA2026_COMMON + [(26_300_000, 0.30), (None, 0.35)],
)

# Net-wealth surcharge bands (% of income tax). Same bands for AY 2025-26 through
# AY 2030-31. Each tuple: (upper_bound_inclusive_or_None, rate).
SURCHARGE_BANDS = [
    (40_000_000, 0.00),    # <= 4 crore
    (100_000_000, 0.10),   # > 4cr to 10cr
    (200_000_000, 0.20),   # > 10cr to 20cr
    (500_000_000, 0.30),   # > 20cr to 50cr
    (None, 0.35),          # > 50 crore
]

# Gratuity (end-of-service benefit) exclusion: ITA 2023 Sixth Schedule Part 1.
# Exempt up to BDT 2.5 crore when received from a government or NBR-approved gratuity
# fund; any excess is taxable as employment income.
GRATUITY_EXEMPT_CAP = 25_000_000   # BDT 2.5 crore

# Return-timing windows for the "windows" rule (Sec 170(1) and Sec 174).
#   kind "incentive": reduction = LOWER of rate x Sec-173 tax and the amount.
#   kind "additional": extra tax = HIGHER of rate x Sec-173 tax and the amount.
FILING_WINDOWS = {
    "early": {"kind": "incentive", "rate": 0.05, "amount": 25_000,
              "label": "1 Jul - 30 Sep (early-filing incentive)"},
    "standard": {"kind": "none", "rate": 0.0, "amount": 0,
                 "label": "1 Oct - 31 Dec (no incentive, no additional tax)"},
    "late_q3": {"kind": "additional", "rate": 0.02, "amount": 3_000,
                "label": "1 Jan - 31 Mar (additional tax)"},
    "late_q4": {"kind": "additional", "rate": 0.05, "amount": 5_000,
                "label": "1 Apr - 30 Jun (additional tax)"},
    "after_year": {"kind": "additional", "rate": 0.10, "amount": 5_000,
                   "label": "after the assessment year, voluntary late return (Sec 174)"},
    "after_notice": {"kind": "additional", "rate": 0.15, "amount": 10_000,
                     "label": "after the assessment year, on a Sec 212(1) notice (Sec 174)"},
}

INCOME_HEADS = ("rent", "agriculture", "business", "capital_gains", "financial", "other")
LOCATIONS = ("dhaka_ctg_cc", "other_cc", "other")


def _slab_tax(taxable_above_threshold: float, bands) -> tuple[float, list]:
    """Apply ordered bands to income above the threshold. Returns (tax, breakdown)."""
    tax = 0.0
    remaining = taxable_above_threshold
    breakdown = []
    for width, rate in bands:
        if remaining <= 0:
            break
        slice_amt = remaining if width is None else min(remaining, width)
        slice_tax = slice_amt * rate
        breakdown.append({
            "band_width": width if width is not None else "balance",
            "rate": rate,
            "amount_taxed": round(slice_amt, 2),
            "tax": round(slice_tax, 2),
        })
        tax += slice_tax
        remaining -= slice_amt
    return tax, breakdown


def _surcharge_rate(net_wealth: float) -> float:
    for upper, rate in SURCHARGE_BANDS:
        if upper is None or net_wealth <= upper:
            return rate
    return SURCHARGE_BANDS[-1][1]


def filing_window_for_date(assessment_year: str, filing_date) -> str:
    """Map a filing date to its return-timing window for a "windows" assessment year.

    The assessment year "2026-27" runs 1 Jul 2026 - 30 Jun 2027. A date after it ends
    maps to "after_year" (use "after_notice" explicitly when filing on a Sec 212 notice).
    """
    if isinstance(filing_date, str):
        filing_date = _dt.date.fromisoformat(filing_date)
    start_year = int(assessment_year.split("-")[0])
    start = _dt.date(start_year, 7, 1)
    if filing_date < start:
        raise ValueError(
            f"Filing date {filing_date} is before AY {assessment_year} opens ({start})."
        )
    if filing_date <= _dt.date(start_year, 9, 30):
        return "early"
    if filing_date <= _dt.date(start_year, 12, 31):
        return "standard"
    if filing_date <= _dt.date(start_year + 1, 3, 31):
        return "late_q3"
    if filing_date <= _dt.date(start_year + 1, 6, 30):
        return "late_q4"
    return "after_year"


def _non_negative(name: str, value) -> float:
    value = float(value or 0)
    if value < 0:
        raise ValueError(f"{name} cannot be negative (got {value:,.2f}).")
    return value


def compute_tax(
    assessment_year: str,
    category: str = "general",
    salary_income: float = 0,
    other_income: Optional[dict] = None,
    eligible_investment: float = 0,
    location: str = "other",          # AY 2025-26 min tax: dhaka_ctg_cc | other_cc | other
    is_new_taxpayer: bool = False,
    net_wealth: float = 0,
    extra_car: bool = False,
    big_house: bool = False,
    tds_paid: float = 0,
    filed_late: bool = False,         # AY 2025-26 only: filed after Tax Day -> no rebate
    gross_receipts: float = 0,        # business/profession gross receipts (turnover tax)
    gratuity_received: float = 0,     # end-of-service gratuity (Sixth Sch. Part 1)
    gratuity_from_approved_fund: bool = True,   # govt / NBR-approved fund -> 2.5cr exemption
    vehicle_advance_tax: float = 0,   # Sec 153 advance tax: non-refundable credit
    disabled_children: int = 0,       # +50,000 threshold per disabled child/dependant
    filing_window: Optional[str] = None,   # AY 2026-27+: see FILING_WINDOWS
    filing_date=None,                 # AY 2026-27+: derive the window from a date
    dividend_income: float = 0,       # AY 2026-27+: 15% flat (Seventh Schedule)
    precious_metal_gain: float = 0,   # AY 2026-27+: gold/silver etc. gains, 5% flat
    turnover_rate: Optional[float] = None,   # AY 2026-27+: override the 1% turnover rate
) -> dict:
    """Compute Bangladesh individual income tax. Returns every intermediate per the
    9-step procedure in references/procedure.md."""

    if assessment_year not in PARAMS:
        raise ValueError(
            f"Unsupported assessment_year {assessment_year!r}; supported: {sorted(PARAMS)}"
        )
    p = PARAMS[assessment_year]
    notes: list[str] = []

    if category not in p["thresholds"]:
        raise ValueError(
            f"Category {category!r} has no threshold for AY {assessment_year}; "
            f"supported: {list(p['thresholds'])}"
        )
    if p["min_tax_area_based"] and location not in LOCATIONS:
        raise ValueError(f"Unknown location {location!r}; supported: {list(LOCATIONS)}")
    if int(disabled_children) != disabled_children or disabled_children < 0:
        raise ValueError("disabled_children must be a whole number, 0 or more.")

    salary_income = _non_negative("salary_income", salary_income)
    eligible_investment = _non_negative("eligible_investment", eligible_investment)
    net_wealth = float(net_wealth or 0)
    tds_paid = _non_negative("tds_paid", tds_paid)
    gross_receipts = _non_negative("gross_receipts", gross_receipts)
    gratuity_received = _non_negative("gratuity_received", gratuity_received)
    vehicle_advance_tax = _non_negative("vehicle_advance_tax", vehicle_advance_tax)
    dividend_income = _non_negative("dividend_income", dividend_income)
    precious_metal_gain = _non_negative("precious_metal_gain", precious_metal_gain)

    # Step 1: threshold (category + disabled-child addition).
    threshold = p["thresholds"][category] + p["disabled_child_extra"] * int(disabled_children)

    # Step 2: salary exemption = lower of 1/3 salary or the year's cap.
    salary_exemption = min(salary_income / 3.0, p["salary_exemption_cap"]) if salary_income else 0.0
    salary_taxable = max(0.0, salary_income - salary_exemption)

    # Step 3: total income = taxable salary + other heads + taxable gratuity (regular
    # rates) + flat-rate income.
    other_income = {k: float(v) for k, v in (other_income or {}).items()}
    other_total = sum(other_income.values())

    # Gratuity: exempt up to 2.5cr from a govt/approved fund; the excess is taxable as
    # employment income. Non-approved fund: conservatively treated as fully taxable.
    if gratuity_received and gratuity_from_approved_fund:
        gratuity_exempt = min(gratuity_received, GRATUITY_EXEMPT_CAP)
    else:
        gratuity_exempt = 0.0
    gratuity_taxable = round(gratuity_received - gratuity_exempt, 2)

    # Flat-rate income (Seventh Schedule). Where the year has no flat rate, dividends go
    # through the slab schedule and precious-metal gains are not taxable as capital gains.
    dividend_rate = p["dividend_rate"]
    metal_rate = p["precious_metal_gain_rate"]
    if precious_metal_gain and metal_rate is None:
        raise ValueError(
            f"precious_metal_gain is not a taxable capital gain for AY {assessment_year} "
            "(gold, silver, etc. became capital assets from AY 2026-27)."
        )
    if dividend_rate is None:
        slab_dividend, flat_dividend = dividend_income, 0.0
    else:
        slab_dividend, flat_dividend = 0.0, dividend_income
    dividend_tax = flat_dividend * (dividend_rate or 0.0)
    precious_metal_tax = precious_metal_gain * (metal_rate or 0.0)
    flat_rate_income = flat_dividend + precious_metal_gain
    flat_rate_tax = dividend_tax + precious_metal_tax

    regular_income = salary_taxable + other_total + gratuity_taxable + slab_dividend
    total_income = regular_income + flat_rate_income

    # Step 4: gross tax = slab schedule on regular income above the threshold, plus
    # flat-rate tax.
    taxable_above = max(0.0, regular_income - threshold)
    slab_tax, slab_breakdown = _slab_tax(taxable_above, p["bands"])
    gross_tax = slab_tax + flat_rate_tax

    # Step 5: Section 78 investment rebate = lowest of three candidates. The income
    # candidate excludes flat-rate (reduced-rate / final-rate) income.
    rb = p["rebate"]
    cand_income = rb["income_rate"] * regular_income
    cand_investment = rb["investment_rate"] * eligible_investment
    cand_cap = rb["cap"]
    rebate_forfeited = bool(filed_late) and p["timing_rule"] == "tax_day"
    if filed_late and p["timing_rule"] != "tax_day":
        raise ValueError(
            f"filed_late applies to AY 2025-26 only. For AY {assessment_year} use "
            f"filing_window (one of {list(FILING_WINDOWS)}) or filing_date."
        )
    rebate = 0.0 if rebate_forfeited else max(0.0, min(cand_income, cand_investment, cand_cap))

    # Step 6: tax after rebate (floored at 0).
    tax_after_rebate = max(0.0, gross_tax - rebate)

    # Step 7: minimum tax. Applies only if total income exceeds the tax-free threshold,
    # and then even when the rebate brings the tax to zero.
    if total_income > threshold:
        if is_new_taxpayer:
            min_tax = p["min_tax"]["new_taxpayer"]
        elif p["min_tax_area_based"]:
            min_tax = p["min_tax"][location]
        else:
            min_tax = p["min_tax"]["default"]
    else:
        min_tax = 0

    # Turnover tax on business/profession gross receipts.
    tv = p["turnover"]
    turnover_tax = 0.0
    turnover_uplift = 0.0
    business_tax_attributed = 0.0
    legacy_floor_tax = 0.0
    if tv["rule"] == "sec163_6":
        if turnover_rate is not None and not (0 <= turnover_rate <= 0.03):
            raise ValueError("turnover_rate must be between 0 and 0.03.")
        if gross_receipts:
            rate = tv["default_rate"] if turnover_rate is None else turnover_rate
            turnover_tax = rate * gross_receipts
            business_income = max(0.0, other_income.get("business", 0.0))
            if regular_income > 0:
                business_tax_attributed = slab_tax * min(1.0, business_income / regular_income)
            turnover_uplift = max(0.0, turnover_tax - business_tax_attributed)
            notes.append(
                "Turnover tax (Sec 163(6)) is compared with the slab tax attributed to "
                "business income in proportion to regular income. The Act does not spell "
                "out the attribution method, so treat a turnover-tax result as an "
                "approximation and confirm it before filing."
            )
    else:
        if turnover_rate is not None:
            raise ValueError(f"turnover_rate does not apply to AY {assessment_year}.")
        if gross_receipts > tv["floor"]:
            legacy_floor_tax = tv["rate"] * gross_receipts

    payable_before_surcharge = max(
        tax_after_rebate + turnover_uplift, min_tax, legacy_floor_tax
    )
    minimum_tax_applied = payable_before_surcharge > tax_after_rebate + turnover_uplift

    # Step 8: net-wealth surcharge = band% x tax after rebate.
    # The 10% band is also triggered by owning >1 motor car OR >8,000 sq ft of house
    # property.
    surcharge_rate = _surcharge_rate(net_wealth)
    if (extra_car or big_house) and surcharge_rate < 0.10:
        surcharge_rate = 0.10
    surcharge = surcharge_rate * tax_after_rebate

    # Step 9: prepaid-tax credits.
    #   Vehicle advance tax (Sec 153) is creditable only against the income tax itself:
    #   it does not absorb the surcharge, and any excess is forfeited (no refund).
    #   Salary/other source tax and advance tax are fully adjustable; an excess is
    #   refundable or can be carried forward.
    nonref_used = min(vehicle_advance_tax, payable_before_surcharge)
    nonrefundable_unused = round(vehicle_advance_tax - nonref_used, 2)
    tax_due = payable_before_surcharge + surcharge
    s173_payable = payable_before_surcharge - nonref_used + surcharge - tds_paid

    # Return-timing adjustment on the Sec 173 tax (AY 2026-27 onward).
    window = None
    filing_adjustment = 0.0
    early_incentive = 0.0
    late_additional = 0.0
    if p["timing_rule"] == "windows":
        if filing_date is not None:
            derived = filing_window_for_date(assessment_year, filing_date)
            notice_ok = filing_window == "after_notice" and derived == "after_year"
            if filing_window and filing_window != derived and not notice_ok:
                raise ValueError(
                    f"filing_window {filing_window!r} does not match filing_date "
                    f"{filing_date} (which falls in {derived!r})."
                )
            window = filing_window or derived
        else:
            window = filing_window or "standard"
        if window not in FILING_WINDOWS:
            raise ValueError(
                f"Unknown filing_window {window!r}; supported: {list(FILING_WINDOWS)}"
            )
        w = FILING_WINDOWS[window]
        base = max(0.0, s173_payable)
        if w["kind"] == "incentive":
            early_incentive = min(w["rate"] * base, w["amount"])
            filing_adjustment = -early_incentive
        elif w["kind"] == "additional":
            if is_new_taxpayer and window in ("late_q3", "late_q4"):
                notes.append(
                    "First-time filers may file up to the 30 June after the income year "
                    "at the normal rate, so no additional tax is added for this window."
                )
            else:
                late_additional = max(w["rate"] * base, w["amount"])
                filing_adjustment = late_additional
        if window in ("after_year", "after_notice"):
            notes.append(
                "Filed after the assessment year: most tax exemptions are lost (salary "
                "exemptions and a few Sixth Schedule items are kept) and delay interest "
                "may apply. Those effects are not computed here."
            )
    elif filing_window or filing_date is not None:
        raise ValueError(
            f"filing_window / filing_date apply from AY 2026-27. For AY {assessment_year} "
            "use filed_late to model filing after Tax Day."
        )

    net_payable = s173_payable + filing_adjustment   # negative -> refundable
    refund = max(0.0, -net_payable)

    if p["status"] != "enacted":
        notes.append(
            f"AY {assessment_year} uses rates legislated in advance by the Finance Act "
            "2026; a later Finance Act can change them."
        )

    return {
        "assessment_year": assessment_year,
        "governing_law": p["governing_law"],
        "status": p["status"],
        "category": category,
        "disabled_children": int(disabled_children),
        "threshold": round(threshold, 2),
        "salary_income": round(salary_income, 2),
        "salary_exemption": round(salary_exemption, 2),
        "salary_taxable": round(salary_taxable, 2),
        "other_income": {k: round(v, 2) for k, v in other_income.items()},
        "gratuity_received": round(gratuity_received, 2),
        "gratuity_from_approved_fund": gratuity_from_approved_fund,
        "gratuity_exempt": round(gratuity_exempt, 2),
        "gratuity_taxable": round(gratuity_taxable, 2),
        "regular_income": round(regular_income, 2),
        "dividend_income": round(dividend_income, 2),
        "dividend_tax": round(dividend_tax, 2),
        "precious_metal_gain": round(precious_metal_gain, 2),
        "precious_metal_tax": round(precious_metal_tax, 2),
        "total_income": round(total_income, 2),
        "taxable_above_threshold": round(taxable_above, 2),
        "slab_breakdown": slab_breakdown,
        "slab_tax": round(slab_tax, 2),
        "gross_tax": round(gross_tax, 2),
        "rebate": round(rebate, 2),
        "rebate_candidates": {
            "income_rate": rb["income_rate"],
            "investment_rate": rb["investment_rate"],
            "pct_of_income": round(cand_income, 2),
            "pct_of_investment": round(cand_investment, 2),
            "cap": cand_cap,
            "filed_late_forfeited": rebate_forfeited,
        },
        "tax_after_rebate": round(tax_after_rebate, 2),
        "minimum_tax": round(min_tax, 2),
        "turnover_tax": round(turnover_tax, 2),
        "business_tax_attributed": round(business_tax_attributed, 2),
        "turnover_tax_uplift": round(turnover_uplift, 2),
        "gross_receipts_min_tax": round(legacy_floor_tax, 2),
        "minimum_tax_applied": minimum_tax_applied,
        "surcharge_rate": surcharge_rate,
        "surcharge": round(surcharge, 2),
        "tax_due": round(tax_due, 2),
        "vehicle_advance_tax": round(vehicle_advance_tax, 2),
        "vehicle_credit_used": round(nonref_used, 2),
        "nonrefundable_unused": nonrefundable_unused,
        "tds_credit": round(tds_paid, 2),
        "tax_payable_s173": round(s173_payable, 2),
        "filing_window": window,
        "filing_window_label": FILING_WINDOWS[window]["label"] if window else None,
        "early_filing_incentive": round(early_incentive, 2),
        "late_filing_additional_tax": round(late_additional, 2),
        "net_payable": round(net_payable, 2),
        "refund": round(refund, 2),
        "notes": notes,
    }


# ---------------------------------------------------------------------------
# Canonical test cases (must pass). Cases marked [NBR] reproduce worked examples
# printed in the NBR Income Tax Guide (Nirdeshika) for the year.
# ---------------------------------------------------------------------------
def _selftest() -> int:
    failures = 0

    def check(label, got, expected):
        nonlocal failures
        if isinstance(expected, str) or expected is None:
            ok = got == expected
            shown = f"got {got!r}, expected {expected!r}"
        else:
            ok = abs(got - expected) < 0.5
            shown = f"got {got:,.2f}, expected {expected:,.2f}"
        if not ok:
            failures += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {shown}")

    def raises(label, fn):
        nonlocal failures
        try:
            fn()
        except ValueError:
            print(f"  [PASS] {label}: rejected as expected")
        else:
            failures += 1
            print(f"  [FAIL] {label}: expected a ValueError")

    print("Running canonical test cases:")

    # Case 1: AY 2026-27, general, salary 800,000 -> exemption 266,666.67, total 533,333.33,
    # gross tax 13,333.33 (133,333.33 above the 400,000 threshold @ 10%).
    r = compute_tax("2026-27", "general", salary_income=800_000)
    check("Case 1 salary_exemption", r["salary_exemption"], 266_666.67)
    check("Case 1 total_income", r["total_income"], 533_333.33)
    check("Case 1 gross_tax", r["gross_tax"], 13_333.33)

    # Case 2: AY 2026-27, salary + rent share, investment 465,000 (10% rebate rate).
    # Total 1,147,470 -> gross 99,494; rebate min(34,424.10; 46,500; 750,000) = 34,424.10.
    r = compute_tax(
        "2026-27", "general", salary_income=1_425_600,
        other_income={"rent": 197_070}, eligible_investment=465_000,
    )
    check("Case 2 total_income", r["total_income"], 1_147_470)
    check("Case 2 gross_tax", r["gross_tax"], 99_494)
    check("Case 2 rebate", r["rebate"], 34_424.10)
    check("Case 2 tax_after_rebate", r["tax_after_rebate"], 65_069.90)

    # Case 3 [NBR 2026-27 guide p.56]: income 5,000,000 -> general 1,110,000;
    # woman / 65+ (threshold 450,000) 1,095,000.
    r = compute_tax("2026-27", "general", other_income={"other": 5_000_000})
    check("Case 3 general gross_tax", r["gross_tax"], 1_110_000)
    r = compute_tax("2026-27", "female", other_income={"other": 5_000_000})
    check("Case 3 female threshold", r["threshold"], 450_000)
    check("Case 3 female gross_tax", r["gross_tax"], 1_095_000)

    # Case 4 [NBR example 17]: two disabled children -> threshold 400,000 + 100,000;
    # income 600,000 -> tax 10,000. Mother (450,000 + 100,000), income 700,000 -> 15,000.
    r = compute_tax("2026-27", "general", other_income={"other": 600_000}, disabled_children=2)
    check("Case 4 father threshold", r["threshold"], 500_000)
    check("Case 4 father gross_tax", r["gross_tax"], 10_000)
    r = compute_tax("2026-27", "female", other_income={"other": 700_000}, disabled_children=2)
    check("Case 4 mother gross_tax", r["gross_tax"], 15_000)

    # Case 5 [NBR example 18]: woman, income 980,000, investment 317,000, source tax 6,400
    # -> gross 64,500; rebate 29,400; after rebate 35,100; payable 28,700.
    r = compute_tax(
        "2026-27", "female", other_income={"other": 980_000},
        eligible_investment=317_000, tds_paid=6_400,
    )
    check("Case 5 gross_tax", r["gross_tax"], 64_500)
    check("Case 5 rebate", r["rebate"], 29_400)
    check("Case 5 tax_after_rebate", r["tax_after_rebate"], 35_100)
    check("Case 5 net_payable", r["net_payable"], 28_700)

    # Case 6 [NBR example 19]: income 680,000, investment 198,000, source tax 5,000
    # -> gross 28,000; rebate 19,800 (investment candidate binds); payable 3,200.
    r = compute_tax(
        "2026-27", "general", other_income={"other": 680_000},
        eligible_investment=198_000, tds_paid=5_000,
    )
    check("Case 6 rebate", r["rebate"], 19_800)
    check("Case 6 net_payable", r["net_payable"], 3_200)

    # Case 7 [NBR guide p.67]: new taxpayer, income 430,000, investment 96,000 -> gross
    # 3,000, rebate 9,600 exceeds it, so the 1,000 new-taxpayer minimum applies.
    r = compute_tax(
        "2026-27", "general", other_income={"other": 430_000},
        eligible_investment=96_000, is_new_taxpayer=True,
    )
    check("Case 7 gross_tax", r["gross_tax"], 3_000)
    check("Case 7 net_payable", r["net_payable"], 1_000)

    # Case 8 [NBR example 23]: salary 1,260,000 -> taxable 840,000; investment 270,000 ->
    # gross 51,000; rebate 25,200; Sec 173 tax 25,800. Filing windows:
    # early 24,510; Jan-Mar 28,800; Apr-Jun 30,800.
    kw = dict(salary_income=1_260_000, eligible_investment=270_000)
    r = compute_tax("2026-27", "general", **kw)
    check("Case 8 total_income", r["total_income"], 840_000)
    check("Case 8 tax_payable_s173", r["tax_payable_s173"], 25_800)
    check("Case 8 standard net_payable", r["net_payable"], 25_800)
    r = compute_tax("2026-27", "general", filing_window="early", **kw)
    check("Case 8 early incentive", r["early_filing_incentive"], 1_290)
    check("Case 8 early net_payable", r["net_payable"], 24_510)
    r = compute_tax("2026-27", "general", filing_date="2027-02-10", **kw)
    check("Case 8 Feb filing window", r["filing_window"], "late_q3")
    check("Case 8 Jan-Mar net_payable", r["net_payable"], 28_800)
    r = compute_tax("2026-27", "general", filing_window="late_q4", **kw)
    check("Case 8 Apr-Jun net_payable", r["net_payable"], 30_800)

    # Case 9 [NBR example 26]: return filed 15 Jul 2027 (after the assessment year).
    # Income 1,790,000, investment 560,000, source tax 4,000 -> gross 237,500; rebate
    # 53,700 (still allowed); Sec 173 tax 179,800; additional 17,980; payable 197,780.
    r = compute_tax(
        "2026-27", "general", salary_income=600_000,
        other_income={"agriculture": 1_350_000, "financial": 40_000},
        eligible_investment=560_000, tds_paid=4_000, filing_date="2027-07-15",
    )
    check("Case 9 gross_tax", r["gross_tax"], 237_500)
    check("Case 9 rebate", r["rebate"], 53_700)
    check("Case 9 filing_window", r["filing_window"], "after_year")
    check("Case 9 additional tax", r["late_filing_additional_tax"], 17_980)
    check("Case 9 net_payable", r["net_payable"], 197_780)

    # Case 10 [NBR example 24]: two cars, income 1,600,000 -> tax 190,000, surcharge 10%
    # = 19,000. Vehicle advance tax 350,000 covers the income tax only: the surcharge
    # stays payable and the unused 160,000 is forfeited.
    r = compute_tax(
        "2026-27", "general", other_income={"other": 1_600_000},
        net_wealth=85_000_000, extra_car=True, vehicle_advance_tax=350_000,
    )
    check("Case 10 gross_tax", r["gross_tax"], 190_000)
    check("Case 10 surcharge", r["surcharge"], 19_000)
    check("Case 10 vehicle_credit_used", r["vehicle_credit_used"], 190_000)
    check("Case 10 nonrefundable_unused", r["nonrefundable_unused"], 160_000)
    check("Case 10 net_payable", r["net_payable"], 19_000)

    # Case 11 [NBR example 25]: income 1,500,000 -> tax 170,000 + surcharge 17,000;
    # vehicle advance tax 162,500 -> net payable 24,500.
    r = compute_tax(
        "2026-27", "general", other_income={"other": 1_500_000},
        net_wealth=85_000_000, extra_car=True, vehicle_advance_tax=162_500,
    )
    check("Case 11 net_payable", r["net_payable"], 24_500)

    # Case 12 [NBR example "Kha", p.103-105]: business owner. Regular income 4,882,500
    # (rent 315,000 + business 4,117,500 + interest 450,000) -> slab tax 1,074,750;
    # dividend 100,000 @ 15% = 15,000; gold gain 300,000 @ 5% = 15,000; total 1,104,750.
    # Turnover 41,000,000 x 1% = 410,000 is below the business tax, so no uplift.
    # Credits: source tax 805,000 + vehicle advance tax 75,000 -> payable 224,750.
    r = compute_tax(
        "2026-27", "general",
        other_income={"rent": 315_000, "business": 4_117_500, "financial": 450_000},
        dividend_income=100_000, precious_metal_gain=300_000,
        gross_receipts=41_000_000, net_wealth=38_000_000,
        tds_paid=805_000, vehicle_advance_tax=75_000,
    )
    check("Case 12 total_income", r["total_income"], 5_282_500)
    check("Case 12 slab_tax", r["slab_tax"], 1_074_750)
    check("Case 12 gross_tax", r["gross_tax"], 1_104_750)
    check("Case 12 turnover_tax", r["turnover_tax"], 410_000)
    check("Case 12 turnover_tax_uplift", r["turnover_tax_uplift"], 0)
    check("Case 12 net_payable", r["net_payable"], 224_750)

    # Case 13: turnover tax binds. Business income 500,000 on turnover 20,000,000 ->
    # slab tax 10,000 (all business); turnover tax 200,000 -> uplift 190,000.
    r = compute_tax(
        "2026-27", "general", other_income={"business": 500_000}, gross_receipts=20_000_000,
    )
    check("Case 13 turnover_tax_uplift", r["turnover_tax_uplift"], 190_000)
    check("Case 13 net_payable", r["net_payable"], 200_000)

    # Case 14: surcharge band edges (NBR surcharge examples 3 and 8): exactly 4 crore
    # -> nil; exactly 20 crore -> 20%.
    r = compute_tax("2026-27", "general", other_income={"other": 500_000}, net_wealth=40_000_000)
    check("Case 14 surcharge at 4 crore", r["surcharge"], 0)
    r = compute_tax("2026-27", "general", other_income={"other": 500_000}, net_wealth=200_000_000)
    check("Case 14 surcharge at 20 crore", r["surcharge"], 2_000)

    # Case 15 [NBR 2025-26 guide p.51]: AY 2025-26, income 5,000,000 -> 1,065,000.
    r = compute_tax("2025-26", "general", other_income={"other": 5_000_000})
    check("Case 15 AY 2025-26 gross_tax", r["gross_tax"], 1_065_000)

    # Case 16: AY 2025-26, general, total income 880,000, Dhaka -> gross 49,500.
    r = compute_tax(
        "2025-26", "general", other_income={"business": 880_000}, location="dhaka_ctg_cc",
    )
    check("Case 16 gross_tax", r["gross_tax"], 49_500)

    # Case 17 [NBR 2025-26 guide p.59]: woman, income 600,000, investment 230,000, Dhaka
    # South -> gross 15,000; rebate 18,000 exceeds it, so the 5,000 minimum applies.
    # Filed after Tax Day the rebate is forfeited -> 15,000.
    kw = dict(other_income={"other": 600_000}, eligible_investment=230_000,
              location="dhaka_ctg_cc")
    r = compute_tax("2025-26", "female", **kw)
    check("Case 17 rebate", r["rebate"], 18_000)
    check("Case 17 net_payable", r["net_payable"], 5_000)
    r = compute_tax("2025-26", "female", filed_late=True, **kw)
    check("Case 17 filed late net_payable", r["net_payable"], 15_000)

    # Case 18: AY 2027-28 mirrors AY 2026-27 (same para Ka schedule).
    r = compute_tax("2027-28", "general", salary_income=800_000)
    check("Case 18 (2027-28 mirrors 2026-27) gross_tax", r["gross_tax"], 13_333.33)
    check("Case 18 status", r["status"], "legislated-forward")

    # Case 19: AY 2028-29 (para Kha): threshold 450,000 and the 35% band above
    # 30,000,000. Income 31,000,000 -> 30,000+60,000+100,000+500,000+7,905,000+350,000.
    r = compute_tax("2028-29", "general", other_income={"other": 31_000_000})
    check("Case 19 AY 2028-29 threshold", r["threshold"], 450_000)
    check("Case 19 AY 2028-29 gross_tax", r["gross_tax"], 8_945_000)

    # Case 20: AY 2030-31 (para Ga): threshold 500,000; woman 550,000.
    r = compute_tax("2030-31", "female", other_income={"other": 850_000})
    check("Case 20 AY 2030-31 female gross_tax", r["gross_tax"], 30_000)

    # Case 21: gratuity within the 2.5cr cap from an approved fund -> fully exempt.
    r = compute_tax(
        "2026-27", "general", salary_income=1_450_000,
        gratuity_received=2_000_000, gratuity_from_approved_fund=True,
    )
    check("Case 21 gratuity_taxable", r["gratuity_taxable"], 0)
    check("Case 21 total_income", r["total_income"], 966_666.67)

    # Case 22: gratuity above the 2.5cr cap -> excess is taxable.
    r = compute_tax(
        "2026-27", "general", gratuity_received=30_000_000, gratuity_from_approved_fund=True,
    )
    check("Case 22 gratuity_taxable", r["gratuity_taxable"], 5_000_000)

    # Case 23: vehicle advance tax only partly usable -> non-refundable, net 0.
    r = compute_tax("2026-27", "general", salary_income=800_000, vehicle_advance_tax=25_000)
    check("Case 23 vehicle_credit_used", r["vehicle_credit_used"], 13_333.33)
    check("Case 23 net_payable", r["net_payable"], 0)

    # Case 24: input validation.
    raises("Case 24 unknown year", lambda: compute_tax("2019-20"))
    raises("Case 24 negative salary", lambda: compute_tax("2026-27", salary_income=-1))
    raises("Case 24 filed_late on a windows year",
           lambda: compute_tax("2026-27", salary_income=800_000, filed_late=True))
    raises("Case 24 filing_window on AY 2025-26",
           lambda: compute_tax("2025-26", salary_income=800_000, filing_window="early"))
    raises("Case 24 july_warrior has no AY 2025-26 threshold",
           lambda: compute_tax("2025-26", "july_warrior", salary_income=800_000))
    raises("Case 24 filing date before the assessment year",
           lambda: compute_tax("2026-27", salary_income=800_000, filing_date="2026-06-30"))

    print()
    if failures == 0:
        print("All canonical test cases passed.")
    else:
        print(f"{failures} check(s) FAILED.")
    return failures


def _cli() -> None:
    ap = argparse.ArgumentParser(description="Bangladesh individual income-tax calculator.")
    ap.add_argument("--selftest", action="store_true", help="run canonical test cases")
    ap.add_argument(
        "--year", default="2026-27", choices=sorted(PARAMS),
        help="assessment year (2026-27 primary; 2027-28 onward are legislated estimates)",
    )
    ap.add_argument(
        "--category", default="general",
        choices=["general", "female", "senior", "disabled", "third_gender",
                 "freedom_fighter", "july_warrior"],
    )
    ap.add_argument("--salary", type=float, default=0, help="gross salary before exemption")
    ap.add_argument("--rent", type=float, default=0, help="rental income after allowed deductions")
    ap.add_argument("--agriculture", type=float, default=0)
    ap.add_argument("--business", type=float, default=0)
    ap.add_argument("--capital-gains", type=float, default=0,
                    help="capital gains taxed at regular rates")
    ap.add_argument("--financial", type=float, default=0,
                    help="interest/profit on deposits and securities (not dividends)")
    ap.add_argument("--other", type=float, default=0)
    ap.add_argument("--dividend", type=float, default=0,
                    help="dividend income (15%% flat from AY 2026-27)")
    ap.add_argument("--precious-metal-gain", type=float, default=0,
                    help="gain on sale of gold/silver/gems (5%% flat from AY 2026-27)")
    ap.add_argument("--investment", type=float, default=0, help="eligible investment")
    ap.add_argument("--disabled-children", type=int, default=0,
                    help="disabled children/dependants (+50,000 threshold each)")
    ap.add_argument("--location", default="other", choices=list(LOCATIONS),
                    help="AY 2025-26 minimum tax area")
    ap.add_argument("--new-taxpayer", action="store_true")
    ap.add_argument("--net-wealth", type=float, default=0)
    ap.add_argument("--extra-car", action="store_true")
    ap.add_argument("--big-house", action="store_true")
    ap.add_argument("--tds", type=float, default=0,
                    help="tax deducted at source plus advance tax already paid")
    ap.add_argument("--filing-window", choices=list(FILING_WINDOWS), default=None,
                    help="AY 2026-27+: when the return is filed")
    ap.add_argument("--filing-date", default=None,
                    help="AY 2026-27+: filing date YYYY-MM-DD (derives the window)")
    ap.add_argument("--filed-late", action="store_true",
                    help="AY 2025-26 only: filed after Tax Day (rebate forfeited)")
    ap.add_argument("--gross-receipts", type=float, default=0,
                    help="business/profession gross receipts (turnover tax check)")
    ap.add_argument("--turnover-rate", type=float, default=None,
                    help="AY 2026-27+: turnover tax rate if not the general 0.01")
    ap.add_argument("--gratuity", type=float, default=0, help="gratuity received (end of service)")
    ap.add_argument(
        "--gratuity-unapproved", action="store_true",
        help="gratuity is NOT from a govt/NBR-approved fund (no 2.5cr exemption)",
    )
    ap.add_argument(
        "--vehicle-advance-tax", type=float, default=0,
        help="Sec 153 advance tax paid at registration/fitness renewal (non-refundable credit)",
    )
    args = ap.parse_args()

    if args.selftest:
        raise SystemExit(1 if _selftest() else 0)

    other = {
        "rent": args.rent,
        "agriculture": args.agriculture,
        "business": args.business,
        "capital_gains": args.capital_gains,
        "financial": args.financial,
        "other": args.other,
    }
    other = {k: v for k, v in other.items() if v}

    try:
        result = compute_tax(
            assessment_year=args.year,
            category=args.category,
            salary_income=args.salary,
            other_income=other,
            eligible_investment=args.investment,
            location=args.location,
            is_new_taxpayer=args.new_taxpayer,
            net_wealth=args.net_wealth,
            extra_car=args.extra_car,
            big_house=args.big_house,
            tds_paid=args.tds,
            filed_late=args.filed_late,
            gross_receipts=args.gross_receipts,
            gratuity_received=args.gratuity,
            gratuity_from_approved_fund=not args.gratuity_unapproved,
            vehicle_advance_tax=args.vehicle_advance_tax,
            disabled_children=args.disabled_children,
            filing_window=args.filing_window,
            filing_date=args.filing_date,
            dividend_income=args.dividend,
            precious_metal_gain=args.precious_metal_gain,
            turnover_rate=args.turnover_rate,
        )
    except ValueError as exc:
        ap.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
