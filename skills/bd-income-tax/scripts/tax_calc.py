#!/usr/bin/env python3
"""
Bangladesh individual income-tax calculator (deterministic, standard library only).

Scope: PERSONAL / individual income tax under the Income Tax Act 2023 as amended by
the annual Finance Act. Supports Assessment Year (AY) 2026-27 (primary), 2025-26, and
2027-28 (legislated via the Finance Ordinance 2025 for two years; mirrors 2026-27).

All rates/thresholds live in PARAMS below so a yearly update touches one place.
This module performs NO network calls. It is the single source of arithmetic for the
bd-income-tax skill — the model must never hand-calculate tax.

Usage:
    from tax_calc import compute_tax
    result = compute_tax("2026-27", "general", salary_income=1_320_000)

CLI:
    python3 tax_calc.py --year 2026-27 --category general --salary 800000
    python3 tax_calc.py --selftest      # run the four canonical test cases
"""

from __future__ import annotations

import argparse
import copy
import json
from typing import Optional

# ---------------------------------------------------------------------------
# Year parameters. Each figure is sourced in references/sources.md.
# Slab "bands" are the widths/rates that apply to income ABOVE the taxpayer's
# tax-free threshold, in order. (The first 0% band of the published schedule is
# represented by the category threshold itself.)
# ---------------------------------------------------------------------------
PARAMS = {
    "2026-27": {
        "governing_law": (
            "Income Tax Act 2023 as amended; rates per Finance Ordinance 2025 and "
            "Finance Bill 2026 (placed in Parliament 11 Jun 2026 — confirm against "
            "the gazetted Finance Act 2026)."
        ),
        "thresholds": {
            "general": 375_000,
            "female": 425_000,
            "senior": 425_000,            # senior citizens 65+
            "disabled": 500_000,
            "third_gender": 500_000,
            "freedom_fighter": 525_000,   # gazetted freedom fighters
            "july_warrior": 525_000,      # gazetted "July Warriors" (2024 uprising)
        },
        # Bands applied to income above the threshold (width, rate). 5% slab abolished.
        "bands": [
            (300_000, 0.10),
            (400_000, 0.15),
            (500_000, 0.20),
            (2_000_000, 0.25),
            (None, 0.30),   # balance
        ],
        "salary_exemption_cap": 500_000,
        "min_tax": {
            # AY 2026-27: flat, location-independent.
            "default": 5_000,
            "new_taxpayer": 1_000,
        },
        "min_tax_area_based": False,
    },
    "2025-26": {
        "governing_law": "Income Tax Act 2023 as amended by the Finance Ordinance 2025.",
        "thresholds": {
            "general": 350_000,
            "female": 400_000,
            "senior": 400_000,
            "disabled": 475_000,
            "third_gender": 475_000,
            "freedom_fighter": 500_000,
            "july_warrior": 525_000,      # gazetted July-uprising injured
        },
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
            # AY 2025-26: area-based (last year of this system).
            "dhaka_ctg_cc": 5_000,   # Dhaka North/South + Chattogram City Corporation
            "other_cc": 4_000,       # other city corporations
            "other": 3_000,          # outside city corporations
            "new_taxpayer": 1_000,
        },
        "min_tax_area_based": True,
    },
}

# AY 2027-28 was legislated together with AY 2026-27 by the Finance Ordinance 2025 (a
# two-year fix: same Tk 375,000 threshold, same 0/10/15/20/25/30% schedule, same flat
# Tk 5,000 minimum tax). Build it from 2026-27 to avoid drift, then override the law note.
PARAMS["2027-28"] = copy.deepcopy(PARAMS["2026-27"])
PARAMS["2027-28"]["governing_law"] = (
    "Income Tax Act 2023 as amended. The Tk 375,000 threshold, the 0/10/15/20/25/30% slab "
    "schedule, and the flat Tk 5,000 minimum tax were legislated via the Finance Ordinance "
    "2025 for BOTH AY 2026-27 and AY 2027-28. They remain subject to amendment by the Finance "
    "Act 2027 (budget ~Jun 2027), so treat this as the best current estimate for AY 2027-28, "
    "not yet a final filing figure."
)

# Net-wealth surcharge bands (% of income tax after rebate). Shared across years.
# Each tuple: (upper_bound_inclusive_or_None, rate).
SURCHARGE_BANDS = [
    (40_000_000, 0.00),    # <= 4 crore
    (100_000_000, 0.10),   # > 4cr to 10cr
    (200_000_000, 0.20),   # > 10cr to 20cr
    (500_000_000, 0.30),   # > 20cr to 50cr
    (None, 0.35),          # > 50 crore
]

REBATE_RATE = 0.15                 # 15% of the eligible amount (Section 78)
REBATE_INCOME_RATE = 0.03          # candidate 1: 3% of total income
REBATE_INVESTMENT_RATE = 0.15      # candidate 2: 15% of allowable investment
REBATE_CAP = 1_000_000             # candidate 3: hard cap

GROSS_RECEIPTS_FLOOR = 40_000_000  # > 4 crore gross receipts triggers 0.25% min tax
GROSS_RECEIPTS_RATE = 0.0025

# Gratuity (end-of-service benefit) exclusion: ITA 2023 Sixth Schedule Part 1, paras 5-6.
# Exempt up to BDT 2.5 crore when received from a government or NBR-approved gratuity fund;
# any excess is taxable as employment income. Cap unchanged through the Finance Ordinance 2025.
GRATUITY_EXEMPT_CAP = 25_000_000   # BDT 2.5 crore


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
    filed_late: bool = False,         # if True, investment rebate is forfeited
    gross_receipts: float = 0,        # for the 0.25% gross-receipts min-tax comparison
    gratuity_received: float = 0,     # end-of-service gratuity (Sixth Sch. Part 1, paras 5-6)
    gratuity_from_approved_fund: bool = True,   # govt / NBR-approved fund -> 2.5cr exemption
    vehicle_advance_tax: float = 0,   # Sec 153 AIT at fitness renewal: non-refundable credit
) -> dict:
    """Compute Bangladesh individual income tax. Returns every intermediate per the
    9-step procedure in references/procedure.md."""

    if assessment_year not in PARAMS:
        raise ValueError(
            f"Unsupported assessment_year {assessment_year!r}; supported: {list(PARAMS)}"
        )
    p = PARAMS[assessment_year]

    if category not in p["thresholds"]:
        raise ValueError(
            f"Unknown category {category!r}; supported: {list(p['thresholds'])}"
        )
    threshold = p["thresholds"][category]

    # Step 2: salary exemption = lower of 1/3 salary or the year's cap.
    salary_exemption = min(salary_income / 3.0, p["salary_exemption_cap"]) if salary_income else 0.0
    salary_taxable = max(0.0, salary_income - salary_exemption)

    # Step 3: total income = taxable salary + other heads + taxable gratuity.
    other_income = other_income or {}
    other_total = sum(float(v) for v in other_income.values())

    # Gratuity (Sixth Schedule Part 1, paras 5-6): exempt up to 2.5cr from a govt/approved
    # fund; the excess is taxable as employment income. Non-approved fund: conservatively
    # treated as fully taxable (the non-approved treatment is not firmly confirmed — flag it).
    gratuity_received = float(gratuity_received or 0)
    if gratuity_received and gratuity_from_approved_fund:
        gratuity_exempt = min(gratuity_received, GRATUITY_EXEMPT_CAP)
    else:
        gratuity_exempt = 0.0
    gratuity_taxable = round(gratuity_received - gratuity_exempt, 2)

    total_income = salary_taxable + other_total + gratuity_taxable

    # Step 4: gross tax via the slab schedule applied above the threshold.
    taxable_above = max(0.0, total_income - threshold)
    gross_tax, slab_breakdown = _slab_tax(taxable_above, p["bands"])

    # Step 5: Section 78 investment rebate = lowest of three candidates (0 if filed late).
    cand_income = REBATE_INCOME_RATE * total_income
    cand_investment = REBATE_INVESTMENT_RATE * eligible_investment
    cand_cap = REBATE_CAP
    if filed_late:
        rebate = 0.0
    else:
        rebate = min(cand_income, cand_investment, cand_cap)

    # Step 6: tax after rebate (floored at 0).
    tax_after_rebate = max(0.0, gross_tax - rebate)

    # Step 7: minimum tax. Only applies if income exceeds the tax-free threshold.
    if total_income > threshold:
        if is_new_taxpayer:
            min_tax = p["min_tax"]["new_taxpayer"]
        elif p["min_tax_area_based"]:
            min_tax = p["min_tax"].get(location, p["min_tax"]["other"])
        else:
            min_tax = p["min_tax"]["default"]
    else:
        min_tax = 0

    # Gross-receipts floor for high-turnover individuals.
    gross_receipts_min = (
        GROSS_RECEIPTS_RATE * gross_receipts if gross_receipts > GROSS_RECEIPTS_FLOOR else 0.0
    )

    payable_before_surcharge = max(tax_after_rebate, min_tax, gross_receipts_min)
    minimum_tax_applied = payable_before_surcharge > tax_after_rebate

    # Step 8: net-wealth surcharge = band% x tax after rebate.
    # The 10% band is also triggered by owning >1 car OR >8,000 sq ft residential property.
    surcharge_rate = _surcharge_rate(net_wealth)
    if (extra_car or big_house) and surcharge_rate < 0.10:
        surcharge_rate = 0.10
    surcharge = surcharge_rate * tax_after_rebate

    # Step 9: apply prepaid-tax credits.
    #   Vehicle advance tax (Sec 153) is non-refundable / minimum-style: creditable only up
    #   to the tax due — any excess is forfeited (no refund, no carry-forward modelled here;
    #   confirm the exact in-year-credit vs carry rule against the gazetted Act).
    #   Salary/other TDS (Sec 86 etc.) is fully adjustable; any excess is refundable.
    tax_due = payable_before_surcharge + surcharge
    nonref = float(vehicle_advance_tax or 0)
    nonref_used = min(nonref, tax_due)
    after_nonref = tax_due - nonref_used
    net_payable = after_nonref - float(tds_paid or 0)   # may go negative -> refundable
    refund = max(0.0, -net_payable)
    nonrefundable_unused = round(nonref - nonref_used, 2)

    return {
        "assessment_year": assessment_year,
        "governing_law": p["governing_law"],
        "category": category,
        "threshold": round(threshold, 2),
        "salary_income": round(salary_income, 2),
        "salary_exemption": round(salary_exemption, 2),
        "salary_taxable": round(salary_taxable, 2),
        "other_income": {k: round(float(v), 2) for k, v in other_income.items()},
        "gratuity_received": round(gratuity_received, 2),
        "gratuity_from_approved_fund": gratuity_from_approved_fund,
        "gratuity_exempt": round(gratuity_exempt, 2),
        "gratuity_taxable": round(gratuity_taxable, 2),
        "total_income": round(total_income, 2),
        "taxable_above_threshold": round(taxable_above, 2),
        "slab_breakdown": slab_breakdown,
        "gross_tax": round(gross_tax, 2),
        "rebate": round(rebate, 2),
        "rebate_candidates": {
            "3pct_total_income": round(cand_income, 2),
            "15pct_investment": round(cand_investment, 2),
            "cap": cand_cap,
            "filed_late_forfeited": filed_late,
        },
        "tax_after_rebate": round(tax_after_rebate, 2),
        "minimum_tax": round(min_tax, 2),
        "gross_receipts_min_tax": round(gross_receipts_min, 2),
        "minimum_tax_applied": minimum_tax_applied,
        "surcharge_rate": surcharge_rate,
        "surcharge": round(surcharge, 2),
        "vehicle_advance_tax": round(nonref, 2),
        "vehicle_credit_used": round(nonref_used, 2),
        "nonrefundable_unused": nonrefundable_unused,
        "tds_credit": round(tds_paid, 2),
        "net_payable": round(net_payable, 2),
        "refund": round(refund, 2),
    }


def _surcharge_rate(net_wealth: float) -> float:
    for upper, rate in SURCHARGE_BANDS:
        if upper is None or net_wealth <= upper:
            return rate
    return SURCHARGE_BANDS[-1][1]


# ---------------------------------------------------------------------------
# Canonical test cases (must pass — see brief §7).
# ---------------------------------------------------------------------------
def _selftest() -> int:
    failures = 0

    def check(label, got, expected):
        nonlocal failures
        ok = abs(got - expected) < 0.5
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"  [{status}] {label}: got {got:,.2f}, expected {expected:,.2f}")

    print("Running canonical test cases:")

    # Case 1: AY 2026-27, general, salary 800,000 -> exemption 266,666.67, total 533,333.33,
    # gross tax 15,833.33.
    r1 = compute_tax("2026-27", "general", salary_income=800_000)
    check("Case 1 salary_exemption", r1["salary_exemption"], 266_666.67)
    check("Case 1 total_income", r1["total_income"], 533_333.33)
    check("Case 1 gross_tax", r1["gross_tax"], 15_833.33)

    # Case 2: AY 2026-27, total income 1,147,470 via heads, investment 465,000 ->
    # gross 104,494, rebate 34,424, after rebate 70,070.
    # Model total income directly through "other" head (rent) to hit 1,147,470.
    r2 = compute_tax(
        "2026-27", "general",
        other_income={"rent": 1_147_470},
        eligible_investment=465_000,
    )
    check("Case 2 gross_tax", r2["gross_tax"], 104_494)
    check("Case 2 rebate", r2["rebate"], 34_424)
    check("Case 2 tax_after_rebate", r2["tax_after_rebate"], 70_070)

    # Case 3: AY 2026-27, female, total income 500,000 -> threshold 425,000, gross 7,500.
    r3 = compute_tax("2026-27", "female", other_income={"other": 500_000})
    check("Case 3 threshold", r3["threshold"], 425_000)
    check("Case 3 gross_tax", r3["gross_tax"], 7_500)

    # Case 4: AY 2025-26, general, total income 880,000, dhaka_ctg_cc -> gross 49,500.
    r4 = compute_tax(
        "2025-26", "general",
        other_income={"business": 880_000},
        location="dhaka_ctg_cc",
    )
    check("Case 4 gross_tax", r4["gross_tax"], 49_500)

    # Case 5: AY 2027-28 mirrors AY 2026-27 (same threshold + schedule).
    r5 = compute_tax("2027-28", "general", salary_income=800_000)
    check("Case 5 (2027-28 mirrors 2026-27) gross_tax", r5["gross_tax"], 15_833.33)

    # Case 6: gratuity within the 2.5cr cap from an approved fund -> fully exempt; total
    # income is unchanged vs no gratuity.
    r6 = compute_tax(
        "2026-27", "general", salary_income=1_450_000,
        gratuity_received=2_000_000, gratuity_from_approved_fund=True,
    )
    check("Case 6 gratuity_taxable", r6["gratuity_taxable"], 0)
    check("Case 6 total_income", r6["total_income"], 966_666.67)

    # Case 7: gratuity above the 2.5cr cap -> excess is taxable.
    r7 = compute_tax(
        "2026-27", "general",
        gratuity_received=30_000_000, gratuity_from_approved_fund=True,
    )
    check("Case 7 gratuity_taxable", r7["gratuity_taxable"], 5_000_000)

    # Case 8: vehicle AIT (Sec 153) only partly usable -> non-refundable, net 0.
    # Tax due 15,833.33; car AIT 25,000 -> 15,833.33 credited, 9,166.67 forfeited.
    r8 = compute_tax("2026-27", "general", salary_income=800_000, vehicle_advance_tax=25_000)
    check("Case 8 vehicle_credit_used", r8["vehicle_credit_used"], 15_833.33)
    check("Case 8 net_payable", r8["net_payable"], 0)

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
        "--year", default="2026-27",
        help="assessment year (2026-27 primary | 2025-26 | 2027-28 legislated, mirrors 2026-27)",
    )
    ap.add_argument("--category", default="general")
    ap.add_argument("--salary", type=float, default=0, help="gross salary before exemption")
    ap.add_argument("--rent", type=float, default=0)
    ap.add_argument("--agriculture", type=float, default=0)
    ap.add_argument("--business", type=float, default=0)
    ap.add_argument("--capital-gains", type=float, default=0)
    ap.add_argument("--financial", type=float, default=0)
    ap.add_argument("--other", type=float, default=0)
    ap.add_argument("--investment", type=float, default=0, help="eligible investment")
    ap.add_argument("--location", default="other")
    ap.add_argument("--new-taxpayer", action="store_true")
    ap.add_argument("--net-wealth", type=float, default=0)
    ap.add_argument("--extra-car", action="store_true")
    ap.add_argument("--big-house", action="store_true")
    ap.add_argument("--tds", type=float, default=0)
    ap.add_argument("--filed-late", action="store_true")
    ap.add_argument("--gross-receipts", type=float, default=0)
    ap.add_argument("--gratuity", type=float, default=0, help="gratuity received (end of service)")
    ap.add_argument(
        "--gratuity-unapproved", action="store_true",
        help="gratuity is NOT from a govt/NBR-approved fund (no 2.5cr exemption)",
    )
    ap.add_argument(
        "--vehicle-advance-tax", type=float, default=0,
        help="Sec 153 advance tax paid at fitness renewal (non-refundable credit)",
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
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
