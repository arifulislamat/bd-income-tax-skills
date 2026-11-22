# Calculation procedure

Run `scripts/tax_calc.py` for all arithmetic, then present results as these numbered steps.
The script returns every intermediate listed here.

1. **Determine assessment year and taxpayer category.** Income year (1 Jul to 30 Jun) → the
   following AY. Default income year FY 2025-26 → **AY 2026-27**. Pick that year's threshold
   (plus 50,000 per disabled child where claimed), slab table, salary cap, and minimum-tax rule
   (`references/ay-2026-27.md` or `ay-2025-26.md`).
2. **Compute each income head.** For salary, subtract the exemption = lower of ⅓ salary or
   the year's cap.
3. **Sum heads → total income.** Add any **taxable gratuity** (gratuity above the BDT 2.5cr
   exempt cap from a govt/approved fund). From AY 2026-27 keep **flat-rate income** (dividends,
   precious-metal gains) separate: it is part of total income but not of the slab base.
4. **Apply the slab schedule** to regular income above the threshold, then add the flat-rate
   tax (15% on dividends, 5% on precious-metal gains) → **gross tax**.
5. **Section 78 rebate** = lowest of {3% of regular total income, the year's % of eligible
   investment, the year's cap}. AY 2026-27: 10% and BDT 750,000. AY 2025-26: 15% and
   BDT 1,000,000, and **no rebate if filed after Tax Day**.
6. **Tax after rebate** = gross tax − rebate (floor at 0).
7. **Minimum tax:** payable = max(tax after rebate, minimum tax). The minimum applies whenever
   total income exceeds the threshold. For a business, also run the **turnover-tax** check
   (AY 2026-27: 1% of gross receipts against the tax on business income).
8. **Net-wealth surcharge** = surcharge% × (tax after rebate), if net wealth is in a band
   (or the more-than-one-car / above-8,000-sq-ft trigger applies → 10%).
9. **Apply prepaid-tax credits** (with certificates) → **tax payable with the return
   (Section 173)**. Vehicle advance tax (Sec 153) is credited first and only against the
   income tax itself: it never absorbs the surcharge and any excess is forfeited. Then subtract
   source tax and advance tax; a negative balance is a refund or carry-forward.
10. **Return-timing adjustment (AY 2026-27 onward)** on the Section 173 tax: early-filing
    incentive (lower of 5% or 25,000) or additional tax for a late window → **net payable**.
    See the timing table in `ay-2026-27.md`.

## Worked example 1 (AY 2026-27): salary with investment

This reproduces Example 23 of the NBR Income Tax Guide 2026-27. `[NBR-Guide-2026]`

- **Salary** gross 1,260,000; exemption = ⅓ = 420,000 (below the 500,000 cap) → income
  **840,000**.
- **Gross tax:** 0 (first 400,000) + 300,000 × 10% = 30,000 + 140,000 × 15% = 21,000
  → **51,000**.
- **Eligible investment:** life insurance 50,000 + DPS 120,000 (150,000 paid, capped) +
  sanchayapatra 100,000 = **270,000**.
- **Rebate** = min(3% × 840,000 = 25,200; 10% × 270,000 = 27,000; 750,000) = **25,200**.
- **Tax payable with the return** = 51,000 − 25,200 = **25,800**.
- **Timing:** filed by 30 Sep 2026 → 25,800 − 1,290 = **24,510**. Filed Oct to Dec →
  **25,800**. Filed Jan to Mar 2027 → 25,800 + 3,000 = **28,800**. Filed Apr to Jun 2027 →
  25,800 + 5,000 = **30,800**.

Reproduce with:
```
python3 scripts/tax_calc.py --year 2026-27 --salary 1260000 --investment 270000 \
    --filing-window early
```

## Worked example 2 (AY 2026-27): salary plus a rent share

Salary + co-owned commercial property; eligible investment 465,000.

- **Salary** gross 1,425,600; exemption = ⅓ = 475,200 (below the 500,000 cap) → **950,400**.
- **Rent:** the taxpayer's share of the property income after allowed deductions is
  **197,070** (work the deductions out with the user from their own figures; see the rent
  rules in `ay-2026-27.md`).
- **Total income** = 950,400 + 197,070 = **1,147,470**.
- **Gross tax:** 0 + (300,000 × 10% = 30,000) + (400,000 × 15% = 60,000) +
  (47,470 × 20% = 9,494) = **99,494**.
- **Rebate** = min(3% × 1,147,470 = 34,424.10; 10% × 465,000 = 46,500; 750,000) = **34,424**.
- **Tax after rebate** = **65,070** (above the 5,000 minimum; no surcharge assumed), then less
  any source tax.

Reproduce with:
```
python3 scripts/tax_calc.py --year 2026-27 --category general \
    --salary 1425600 --rent 197070 --investment 465000
```
(Passing the salary as gross lets the script apply the ⅓ exemption; the 197,070 is the
taxpayer's post-deduction property share.)
