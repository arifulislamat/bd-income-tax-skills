---
name: bd-income-tax
description: >-
  Compute and explain Bangladesh individual (personal) income tax under the
  Income Tax Act 2023 and the current Finance Act — tax slabs, tax-free
  thresholds (including women, senior citizens, persons with disabilities,
  third-gender, freedom fighters), salary exemption, the Section 78 investment
  rebate, minimum tax, net-wealth surcharge, TDS credit, filing/PSR rules, Tax
  Day, and penalties. Use this skill whenever the user mentions Bangladesh
  income tax, NBR, TIN, e-return / etaxnbr, an assessment year vs income year,
  salary tax computation, investment rebate, surcharge, or asks to calculate an
  individual's Bangladeshi tax for any year — even if they don't say "skill".
---

# Bangladesh individual income tax

Compute and explain **personal/individual** Bangladesh income tax. Scope is individuals
only — **not** corporate tax or VAT. All arithmetic is done by `scripts/tax_calc.py`; never
hand-calculate.

## 1. Determine the assessment year first

Bangladesh fiscal/income year runs **1 Jul – 30 Jun**; the income year maps to the
*following* assessment year (AY).

| Income year | Assessment year | Governing law | General threshold |
|---|---|---|---|
| 1 Jul 2024 – 30 Jun 2025 | **AY 2025-26** | Finance Ordinance 2025 | 350,000 |
| 1 Jul 2025 – 30 Jun 2026 | **AY 2026-27** (primary) | ITA 2023 + Finance Bill 2026 | 375,000 |

- **Default:** if the user gives a current salary/income with no year, assume income year
  FY 2025-26 → **AY 2026-27**.
- **State the assessment year and governing law at the top of every answer.**
- Note that FY 2026-27 is still a **Finance Bill** (placed 11 Jun 2026) until gazetted as the
  Finance Act 2026 — say so.

## 2. Read the right reference file (progressive disclosure)

Read **only** the file for the relevant year, plus shared files as needed:

- `references/ay-2026-27.md` — AY 2026-27 slabs, thresholds, salary cap, rebate, min tax, surcharge.
- `references/ay-2025-26.md` — prior-year figures (note the 5% slab still applies that year).
- `references/procedure.md` — the ordered 9-step procedure + worked example.
- `references/filing.md` — TIN, PSR, e-return, forms, Tax Day, penalties.
- `references/sources.md` — source keys; cite the source for every rate/threshold.

## 3. Always run the calculator for any number

Never compute tax yourself. Call:

```
python3 scripts/tax_calc.py --year 2026-27 --category general --salary 1320000 [...]
```

Or import `compute_tax(...)`. Key inputs: `--year`, `--category`
(`general|female|senior|disabled|third_gender|freedom_fighter|july_warrior`), income heads
(`--salary` gross, `--rent`, `--agriculture`, `--business`, `--capital-gains`, `--financial`,
`--other`), `--investment`, `--location` (AY 2025-26 min tax: `dhaka_ctg_cc|other_cc|other`),
`--new-taxpayer`, `--net-wealth`, `--extra-car`, `--big-house`, `--tds`, `--filed-late`,
`--gross-receipts`. Run `--selftest` to confirm the four canonical results.

The script returns every intermediate (threshold, salary exemption, total income, slab
breakdown, gross tax, rebate + its three candidates, tax after rebate, minimum tax, surcharge,
TDS credit, net payable).

## 4. Present results as the numbered procedure

Follow `references/procedure.md` steps 1–9 in order. Use **tables** for slabs, rebate
candidates, and surcharge bands. **Cite the source** (e.g. `[FB-2026]`, `[ITA-2023]`) for
every rate and threshold you state.

## 5. Worked example (AY 2026-27)

Salary gross 1,425,600 + 56.25% share of commercial rent (net 197,070), investment 465,000:
- Salary exemption ⅓ = 475,200 (< 500,000 cap) → salary income 950,400.
- Total income 1,147,470 → gross tax **104,494**.
- Rebate = min(34,424; 69,750; 1,000,000) → **34,424**. Tax after rebate **70,070**.

```
python3 scripts/tax_calc.py --year 2026-27 --salary 1425600 --rent 197070 --investment 465000
```

## 6. Guardrails

- Individual tax only; deterministic script for all math; **no network calls**.
- Every numeric output carries the assessment year and a source citation.
- Figures marked **⚠️ unverified** in the references (DPS cap, agriculture deemed-cost %,
  solely-agricultural exemption, delay-interest rate) are **not** used by the calculator —
  present them only with the caveat to confirm against the gazetted Act.

## 7. Always close with the disclaimer

> Informational only; not professional tax advice. Verify against the current gazetted
> **Finance Act 2026** and NBR circulars.
