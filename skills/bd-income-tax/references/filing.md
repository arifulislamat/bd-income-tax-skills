# Filing: TIN, PSR, e-return, forms, deadlines, penalties

`[ITA-2023]` `[NBR]` `[eReturn]` `[TIN]` unless otherwise tagged.

## TIN

- 12-digit **e-TIN** at `secure.incometax.gov.bd`. Resident individuals self-register with
  **NID + biometric verification**.

## Who must file

- Taxable income exceeds the threshold; OR assessed in any of the prior three years;
- Company shareholder-director / executive employee; firm partner; government employee;
- Non-resident with a permanent establishment;
- Anyone required to register or to furnish PSR.

## PSR — Proof of Submission of Return (Section 264)

Required for **43 services**, e.g. credit card, trade licence, savings certificate
> BDT 500,000, loans, and more.

## e-Return portal — `etaxnbr.gov.bd`

Register with TIN + **biometrically-registered mobile** (drop the leading zero) + **OTP**,
set a password. Then: Return Submission → fill heads → rebate/expenses/assets → auto-compute
→ pay via **a-challan** → download acknowledgement / PSR.

**Online filing is mandatory for individuals from AY 2025-26** (limited exceptions: age 65+,
special needs, approved technical issues).

## Forms

| Form | Purpose |
|---|---|
| **IT-11GA** | Individual return |
| **IT-10B** | Statement of assets & liabilities — mandatory if gross wealth > BDT 40 lakh, or for company directors / car owners / city-corporation house owners |
| **IT-10BB** | Lifestyle / expenditure statement |

## Tax Day & deadlines

- **Tax Day: 30 November** following the income year. (AY 2025-26 was extended to
  **31 Dec 2025**.)
- **From FY 2026-27, year-round filing was introduced** — but late filing still carries
  interest/penalty and forfeits the investment rebate for that year. `[FB-2026]`

## Penalties

- **Non-filing:** 10% of tax on last assessed income (min **BDT 1,000**) + **BDT 50/day** for
  continuing default.
- **Under-reporting:** up to **1.5× tax** (Section 72(3)).
- **Late filing** also forfeits the investment rebate for that year (`filed_late=True` in the
  calculator → rebate 0) and triggers delay interest of **~2%/month — ⚠️ unverified
  rate/section; confirm against the gazetted Act.**

## Tax already paid — credits vs deductions

A common confusion: tax *already paid during the year* is a **prepayment of your own tax**,
credited against the final bill — it does **not** reduce taxable income the way an exemption or
the investment rebate does. "Buying a car" or "paying TDS" does not lower your tax; it pre-pays it.

- **Salary TDS** — **Section 86**, deduction from employment income at the *average rate* on
  estimated annual income. Fully adjustable; any **excess is refundable**. *(`tax_calc.py`:
  `--tds`.)* `[ITA-2023]` `[S86]`
- **Vehicle advance tax** — **Section 153**, a fixed amount collected at registration / fitness
  renewal by engine capacity (BDT 25,000 up to 1500cc … BDT 200,000 over 3500cc; microbus
  30,000). It is **adjustable but non-refundable** — treated as minimum tax for that notional
  income, so any **excess is forfeited**, not refunded (§153(6)–(7)). Owning **two or more**
  vehicles raises the advance tax by **+50% per additional vehicle**. *(`tax_calc.py`:
  `--vehicle-advance-tax`.)* `[S153]` `[SDTT]`
- **Dividend / interest WHT** — dividend WHT is **minimum tax and non-refundable**. `[ITA-2023]`

> Separate from the above (a tax on *wealth*, not a credit): owning **more than one car** also
> trips the **10% net-wealth surcharge** band, and a **non-adjustable environmental surcharge**
> applies to multiple-vehicle owners at registration/fitness renewal (EVs exempt from AY
> 2026-27). Don't conflate these with the §153 advance-tax credit above. `[FB-2026]` `[VATax]`

To claim a credit: report the income **and** the tax withheld, and keep the deduction
certificate / a-challan.

## Disclaimer (embed in every answer)

> Informational only; not professional tax advice. Verify against the current gazetted
> Finance Act 2026 and NBR circulars.
