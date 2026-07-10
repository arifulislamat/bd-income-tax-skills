# Sources

Every rate/threshold in the reference files is tagged with one of the source keys below
(e.g. `[ITA-2023]`, `[FA-2026]`, `[PwC]`). Always cite the source for a figure when you
present it. The FY 2026-27 measures are now the **Finance Act 2026** (Finance Bill 2026
passed by Parliament, effective 1 Jul 2026); the general tax-free threshold was raised to
**Tk 400,000** on passage. Still tell users to confirm against the official gazette and
current NBR circulars.

## Primary / official

- **`[ITA-2023]`** Income Tax Act 2023 (আয়কর আইন, ২০২৩), Act No. XII of 2023 — the standing
  statute; repealed the Income Tax Ordinance 1984.
  `https://nbr.gov.bd/uploads/acts/Income_tax_act_2023.pdf`
- **`[ITA-2023-6Sch]`** Income Tax Act 2023, **Sixth Schedule** — Part 1 (exclusions from total
  income: gratuity 2.5cr at paras 5 (govt) & 6 (approved fund), pension, provident/gratuity/
  pension-fund contributions) and Part 3 (eligible investments for the Section 78 rebate).
  `http://bdlaws.minlaw.gov.bd/act-1429/act-part-print-541.html`
- **`[S86]`** Income Tax Act 2023, **Section 86** — deduction at source from income from
  employment (salary TDS at the average rate; adjustable, excess refundable). Was §50 of the
  1984 Ordinance. `https://www.taxvatpoint.com/income-tax-act-2023-section-86/`
- **`[S153]`** Income Tax Act 2023, **Section 153** — collection of advance tax from motor-vehicle
  owners at registration/fitness renewal (fixed by CC; +50% per additional vehicle;
  non-refundable per §153(6)–(7)). Was §68B of the 1984 Ordinance.
  `https://www.taxvatpoint.com/income-tax-act-2023-section-153/`
- **`[NBR]`** National Board of Revenue — `https://nbr.gov.bd`
- **`[eReturn]`** e-Return portal — `https://etaxnbr.gov.bd`
- **`[TIN]`** e-TIN registration — `https://secure.incometax.gov.bd`
- **`[FA-2026]`** Finance Act 2026 / FY2026-27 budget (Finance Bill placed 11 Jun 2026, passed
  by Parliament with the general tax-free threshold raised from Tk 375,000 to **Tk 400,000**):
  - Finance Bill passed, threshold set at Tk 4 lakh — Dhaka Tribune,
    `https://www.dhakatribune.com/business/413915/finance-bill-2026-passed-with-structural-revisions`
  - Threshold set at Tk 4 lakh for FY2026-27 — The Daily Star,
    `https://www.thedailystar.net/business/bangladesh-budget-2025-26/news/finance-bill-passed-tax-free-income-threshold-set-tk-4-lakh-fy2026-27-4211511`
  - Original bill (Tk 375,000 proposal) — BSS, `https://bssnews.net/national-budget-2026-2027/394898`;
    Prothom Alo, `https://en.prothomalo.com/business/local/0sug1clq5v`
- **`[FO-2025]`** Finance Ordinance 2025 / FY2025-26 (interim govt):
  - Prothom Alo — `https://en.prothomalo.com/business/local/4nttx2jgti`
  - ICAB summary — `https://icab.org.bd`

## Authoritative secondary (structure & worked example)

- **`[PwC]`** PwC Worldwide Tax Summaries — Bangladesh Individual (residence, deductions,
  tax administration, sample calculation showing the AY 2026-27 slab structure):
  `https://taxsummaries.pwc.com/bangladesh/individual/`
- **`[DailyStar]`** Surcharge bands — The Daily Star,
  `https://thedailystar.net/business/news/how-bangladeshs-surcharge-and-wealth-tax-system-works-4013321`
- **`[Ramco]`** Minimum-tax change & salary cap — `https://ramco.com/payce/payroll-compliance-bangladesh`
- **`[TaxpertBD]`** Personal tax changes — `https://taxpertbd.com/personal-tax-changes-2025/`
- **`[SDTT]`** SDTT Academy — vehicle advance tax / multiple-vehicle (>1 car) surcharge trigger.
  `https://www.sdttacademy.com/blog/income-tax-in-bangladesh`
- **`[VATax]`** VATax BD — Finance Ordinance 2025 changes, incl. the non-adjustable environmental
  surcharge. `https://vataxbd.com/key-changes-in-the-finance-ordinance-2025-of-bangladesh/`
- **`[bdtaxation]`** ITA 2023 section text, incl. the gratuity 2.5cr exclusion.
  `https://bdtaxation.com/tax-act-section/435`

## Caveat tag

Figures marked **⚠️ unverified** were flagged in the build brief as not fully confirmed
against the gazetted law. They appear only in prose, never in `scripts/tax_calc.py`, and
must be presented with the caveat to confirm against the gazetted Finance Act 2026.
