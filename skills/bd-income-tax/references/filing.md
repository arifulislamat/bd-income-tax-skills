# Filing: TIN, PSR, e-return, forms, timing, penalties

`[ITA-2023]` `[FA-2026]` `[NBR-Guide-2026]` unless otherwise tagged. To help someone fill the
online return in a browser, read `e-return-browser.md`.

## TIN

- 12-digit **e-TIN** at `secure.incometax.gov.bd`. Resident individuals self-register with
  **NID + biometric verification**.

## Who must file

- Total income exceeds the tax-free threshold; OR assessed to tax in any of the prior three
  years;
- Shareholder-director or shareholder-employee of a company; partner of a firm; executive or
  management employee of a business; public servant;
- Non-resident with a permanent establishment;
- Anyone with tax-exempt or reduced-rate income, anyone required to register as a taxpayer
  (Section 261), and anyone who needs proof of return submission for a listed service.

Non-residents other than non-resident Bangladeshis are outside the mandatory list.

## PSR: Proof of Submission of Return (Section 264)

Required when taking a long list of services (the 2026-27 guide lists **46**), for example a
loan above BDT 2,000,000, import/export registration, trade licence renewal in a city
corporation or municipality, land or flat registration, and professional body membership.
Verify a PSR on the e-Return site ("ReturnVerify/PSR").

## e-Return portal: `etaxnbr.gov.bd`

Register with TIN + a mobile SIM **biometrically registered to your own NID** + **OTP**, then
set a password. The return then runs through seven steps: Assessment → Income → Rebate →
Expenditure → Assets & Liabilities → Tax & Payment → Return View → submit. The acknowledgement
and tax certificate are issued instantly. Full walkthrough: `e-return-browser.md`.

**Online filing is mandatory for individuals** (NBR Special Order 1/2026, 28 Jun 2026), except:
taxpayers aged 65 or older; physically incapable or special-needs taxpayers (with a
certificate); Bangladeshi taxpayers living abroad; representatives of a deceased taxpayer; and
foreign nationals working in Bangladesh. These groups may still file online. Anyone else who
cannot register may file on paper only with the approval of the Additional or Joint
Commissioner of Taxes.

## Forms

| Form | Purpose |
|---|---|
| **IT-11GA (2023)** | Individual return |
| **IT-GHA (2023)** | One-page return. Allowed only if **all** hold: taxable income up to BDT 500,000; total wealth up to BDT 5,000,000; no motor vehicle; no house or flat in a city corporation; no assets abroad; not a shareholder-director |
| **IT-10B (2023)** | Statement of assets, liabilities and expenses. Mandatory for public servants; for gross wealth above **BDT 5,000,000**; and, below that, for anyone who owned a motor vehicle, invested in a house or flat in a city corporation, owns assets abroad, or is a shareholder-director |
| **IT-10BB (2023)** | Lifestyle / expenditure statement |

## When to file (AY 2026-27 onward)

There is no single "Tax Day" deadline any more. An individual can file at any time in the
assessment year (1 Jul 2026 to 30 Jun 2027 for AY 2026-27) and the amount payable shifts by
window. See the full table in `ay-2026-27.md`.

```
Jul-Sep 2026        Oct-Dec 2026     Jan-Mar 2027       Apr-Jun 2027       after 30 Jun 2027
5% off (max 25k)    no change        +2% (min 3,000)    +5% (min 5,000)    +10% (min 5,000)
```

- The calculator applies this through `--filing-window` or `--filing-date`.
- A statutory "National Tax Day" still exists as an awareness day. It is not a deadline.
- **AY 2025-26** used the old rule: Tax Day 30 Nov 2025 (later extended), and a late return
  lost the investment rebate. See `ay-2025-26.md`.

## After the assessment year (Section 174)

- Voluntary late return: additional tax = higher of **10%** of the tax payable with the return
  or **BDT 5,000**. After a Section 212(1) notice: higher of **15%** or **BDT 10,000**.
- Most tax exemptions are lost (salary exemptions and a short list of Sixth Schedule items are
  kept). The investment rebate is still allowed.
- Delay interest is charged at a rate 50% higher. ⚠️ unverified: the base rate (commonly
  quoted as 2% a month).
- Not filing at all can also bring a penalty under Section 266, disconnection of utilities,
  and trouble drawing salary. ⚠️ unverified: the penalty amounts (earlier guidance: 10% of the
  last assessed tax, minimum BDT 1,000, plus BDT 50 a day).

## Amending a return

An error found after filing can be fixed with an amended return online, **once**, within
**180 days** of filing.

## Tax already paid: credits vs deductions

A common confusion: tax *already paid during the year* is a **prepayment of your own tax**,
credited against the final bill. It does **not** reduce taxable income the way an exemption or
the investment rebate does. "Buying a car" or "paying TDS" does not lower your tax; it pre-pays
it.

- **Source tax (TDS)** on salary, bank interest, sanchayapatra interest, dividends, imports
  and so on is fully adjustable. From AY 2026-27 any **excess is refundable** or can be carried
  forward (Section 163 as replaced by the Finance Act 2026). *(`tax_calc.py`: `--tds`.)*
- **Advance tax** paid in instalments (Section 154) is credited the same way; include it in
  `--tds`.
- **Vehicle advance tax** (Section 153), paid at registration or fitness renewal (table in
  `ay-2026-27.md`), is **adjustable but not refundable**. It is credited against the income
  tax only: if it exceeds the income tax, nothing more is due on the income, the excess is
  forfeited, and any surcharge is still payable on top. Only tax paid between 1 Jul and 30 Jun
  of the income year counts, and the a-challan must be claimed with the return.
  *(`tax_calc.py`: `--vehicle-advance-tax`.)*
- **Earlier refund:** a refund due from a previous year can be set against this year's tax.

> Separate from the above: owning **more than one car** also trips the **10% net-wealth
> surcharge** band and the **environmental surcharge**, which is never refundable or
> adjustable. Don't conflate these with the Section 153 advance-tax credit.

To claim a credit: report the income **and** the tax withheld, and keep the deduction
certificate or a-challan. On the e-Return site, credits are claimed in the e-Return Ledger.

## Disclaimer (embed in every answer)

> Informational only; not professional tax advice. Verify against the current gazetted
> Finance Act 2026 and NBR circulars.
