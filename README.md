# bd-income-tax-skills

An Agent Skill for **Bangladesh individual (personal) income tax**. It gives an AI agent the
data and a deterministic calculator to answer Bangladesh personal income-tax questions for a
given assessment year — tax slabs, tax-free thresholds, salary exemption, the Section 78
investment rebate, minimum tax, net-wealth surcharge, filing rules, and penalties.

## Quick start

```bash
python3 bd-income-tax/scripts/tax_calc.py --selftest
python3 bd-income-tax/scripts/tax_calc.py --year 2026-27 --category general --salary 1320000
```

## Disclaimer

Informational only; **not professional tax advice.** Verify against the current gazetted
Finance Act and NBR circulars (`nbr.gov.bd`). Individual/personal tax scope only — not
corporate tax or VAT.

## License

[MIT](./LICENSE).
