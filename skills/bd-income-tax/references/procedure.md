# Calculation procedure

Run `scripts/tax_calc.py` for all arithmetic, then present results as these numbered steps.
The script returns every intermediate listed here.

1. **Determine assessment year and taxpayer category.** Income year (1 Jul – 30 Jun) → the
   following AY. Default income year FY 2025-26 → **AY 2026-27**. Pick that year's threshold,
   slab table, salary cap, and min-tax rule (`references/ay-2026-27.md` or `ay-2025-26.md`).
2. **Compute each income head.** For salary, subtract the exemption = lower of ⅓ salary or
   the year's cap.
3. **Sum heads → total income.** Add any **taxable gratuity** (gratuity above the BDT 2.5cr
   exempt cap from a govt/approved fund; see `ay-2026-27.md`).
4. **Apply the slab schedule** to income above the threshold → **gross tax**.
5. **Section 78 rebate** = 15% × lowest of {3% of total income, 15% of eligible investment,
   1,000,000}. **No rebate if the return is filed after Tax Day.**
6. **Tax after rebate** = gross tax − rebate (floor at 0).
7. **Minimum tax:** payable = max(tax after rebate, minimum tax for the year/location). For
   gross receipts > BDT 40,000,000, also compare 0.25% of gross receipts.
8. **Net-wealth surcharge** = surcharge% × (tax after rebate), if net wealth is in a band
   (or the >1-car / >8,000 sq ft trigger applies → 10%).
9. **Apply prepaid-tax credits** (with certificates) → **net tax payable**. Credit
   *non-refundable* items first — vehicle advance tax (Sec 153) and dividend WHT are
   creditable only up to the tax due; any excess is forfeited. Then subtract *refundable*
   salary/other TDS (Sec 86); a negative balance is a refund. See `references/filing.md`.

## Worked example (AY 2026-27)

Salary + co-owned commercial property; eligible investment 465,000.

- **Salary** gross 1,425,600; exemption = ⅓ = 475,200 (< 500,000 cap) → salary income **950,400**.
- **House property:** 516,000 − 30% repair (154,800) − municipal (9,072) − holding (1,782)
  = 350,346; taxpayer's 56.25% share = **197,070**.
- **Total income** = 950,400 + 197,070 = **1,147,470**.
- **Gross tax:** 0 + (300,000×10% = 30,000) + (400,000×15% = 60,000) + (72,470×20% = 14,494)
  = **104,494**.
- **Rebate** = min(3%×1,147,470 = 34,424; 15%×465,000 = 69,750; 1,000,000) = **34,424**.
- **Tax after rebate** = **70,070**. (Above the 5,000 minimum; no surcharge assumed.) Then
  less any TDS.

Reproduce with:
```
python3 scripts/tax_calc.py --year 2026-27 --category general \
    --salary 1425600 --rent 197070 --investment 465000
```
(Passing the salary as gross 1,425,600 lets the script apply the ⅓ exemption; the 197,070 is
the taxpayer's post-deduction property share.)
