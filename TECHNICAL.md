# Technical notes

This is the technical companion to the [README](README.md). It covers the original study, the data, the rules,
every test statistic and how to reproduce the results. All tables are in [results/FINDINGS.md](results/FINDINGS.md).

## The original study

Eric Maskin and John Riley, "Monopoly with Incomplete Information," *RAND Journal of Economics* 15(2), Summer 1984,
pp. 171–196. A theory paper with no data. A seller with constant marginal cost $`c`$ faces buyers indexed by a
one-dimensional taste $`v \sim F`$ and offers a menu of quantity-payment pairs. The headline results are
Proposition 1 (every type but the highest buys where its demand price exceeds $`c`$), Proposition 6 (under
condition (30) the unit price $`T(q)/q`$ declines everywhere) and Proposition 7 (bunching where the virtual type is
not monotone). On p. 184 the authors state that utility multipart tariffs "almost invariably" offer lower unit
prices for greater consumption. With vertically parallel demand $`p(q;v) = v - h(q)`$ (their Example 1) the optimum
is

```math
h\big(q^*(v)\big) = J(v) - c, \qquad J(v) = v - \frac{1 - F(v)}{f(v)}, \qquad p\big(q^*(v);v\big) - c = \frac{1 - F(v)}{f(v)}
```

## Headline results

| Prediction | Test | Result |
|---|---|---|
| Unit price falls with use (Prop. 6) | Household log price on log use, within state | $`\hat\beta = -0.138`$ (0.005), N = 18,481 |
| Unit price falls with use (Prop. 6) | Share of residential customers whose tariff's T(q)/q is lower at 1,500 than 500 kWh | 87.1% of 118.4 million |
| Marginal price falls with use | Customer-weighted shape of residential tiers | 12.8% declining, 46.5% flat, 34.4% inclining, 6.3% mixed |
| Marginal price falls with use | Next-kWh price lower / higher at 1,500 than 500 kWh | 19.0% / 29.9% of customers |
| Top buyers near cost (Prop. 1) | National average price minus resale price, by class | R 10.90¢, C 6.65¢, I 2.30¢ |
| Top buyers near cost (Prop. 1) | Within-utility log price on log use per customer | $`\hat\gamma = -0.084`$ (0.004), 208 utilities |
| Extension: screening needs a profit motive | Ratio of unit price at 1,500 to 500 kWh on ownership | Cooperative $`\hat\theta_1 = -0.112`$ (0.012); public $`-0.019`$ (0.013) |

## Data

All files are in `data/raw/` except the two large downloads, which the scripts fetch and slim on first run.

- `usurdb_slim.csv.gz`: OpenEI Utility Rate Database (apps.openei.org/USURDB/download/usurdb.csv.gz), bulk file
  downloaded 2026-11-01, residential, commercial and industrial tariffs only, with the identifiers, dates, fixed and
  minimum charges, energy schedules and energy tier columns. 52,565 tariffs, 2,816 utility IDs.
- `recs2020_slim.csv.gz`: EIA 2020 Residential Energy Consumption Survey public file v7 (`recs2020_public_v7.csv`),
  columns DOEID, NWEIGHT, NWEIGHT1–NWEIGHT60, state_postal, KWH, DOLLAREL.
- `Sales_Ult_Cust_2025.xlsx` and `Operational_Data_2025.xlsx`: EIA Form 861, 2025 final release
  (eia.gov/electricity/data/eia861/zip/f8612025.zip).
- `ice_electric-2025final.xlsx`: EIA wholesale electricity market data, 2025 ICE next-day peak trades at seven hubs
  (two of them, Indiana and PJM West, are real-time peak products), averaged over trading days.

## Method

Rules fixed before computing any result:

- **In force.** A tariff counts if its end date is missing or after 2026-11-01, no other tariff lists it as
  superseded, and it was updated within 730 days of the newest tariff for the same utility and sector.
- **Standard.** Tariff names matching a fixed list of optional and special-purpose words (time-of-use, EV, net
  metering, solar, lighting, demand, water heating, pilot and others in `SPECIAL`) are dropped. Where a utility lists
  bundled or standard-offer versions, its delivery-only versions are dropped.
- **Shape.** Energy rate plus adjustment, tier by tier, in every period. Declining if all multi-tier periods are
  non-increasing with at least one strict drop; inclining if the reverse; mixed if one period's tiers both rise and fall or periods disagree; flat otherwise.
- **Bills.** For each month, the period used on weekdays; tariffs whose period changes within a day are not priced.
  Tier limits in kWh per day are multiplied by 30.42. Bill = fixed charge (dollars per day × 30.42 where needed) +
  energy charges, raised to any monthly minimum (daily and yearly minimums are ignored), averaged over twelve months. Demand charges are not priced.
- **Weights.** Each utility's standard tariffs count equally within the utility; utilities are weighted by 2025
  bundled plus delivery customers in the sector from Form 861. Short-form filers carry no weight.
- **Wholesale price.** Revenue from sales for resale divided by sales for resale, for utilities with at least
  10,000 MWh of resale. The national figure pools every such Form 861 filer, not only bundled ones.
- **Ownership groups.** Investor owned; cooperative; public (municipal, political subdivision, state, federal).

The estimating equations, with $`i`$ households, $`s`$ states, $`u`$ utilities and $`k`$ customer classes:

```math
\begin{aligned}
\ln\!\Big(\frac{T_{is}}{q_{is}}\Big) &= \alpha_s + \beta \ln q_{is} + \varepsilon_{is} \\
\ln \bar{p}_{uk} &= \alpha_u + \gamma \ln \bar{q}_{uk} + \varepsilon_{uk} \\
\frac{T_u(1500)/1500}{T_u(500)/500} &= \theta_0 + \theta_1\,\text{Coop}_u + \theta_2\,\text{Public}_u + \varepsilon_u
\end{aligned}
```

The household equation is weighted by NWEIGHT; its standard errors use the RECS 2020 jackknife, with the
coefficient taken from EIA's microdata guide.

```math
\widehat{V}(\hat\beta) = \frac{59}{60} \sum_{r=1}^{60} \big(\hat\beta_r - \hat\beta\big)^2
```

The class equation is OLS with errors clustered by utility. The ownership equation is OLS (and WLS by customers) with
HC1 errors. The inverse hazard of monthly household use is computed from a weighted Gaussian kernel density of log
use; the virtual type $`q - (1 - G(q))/g(q)`$ is checked for monotonicity between the 1st and 99th percentiles.

## Full test statistics

| Test | Estimate | SE | 95% CI | N |
|---|---|---|---|---|
| β, household log price on log use, state effects | −0.1384 | 0.0051 | [−0.1483, −0.1284] | 18,481 |
| β, same, no state effects | −0.2122 | 0.0049 | [−0.2218, −0.2027] | 18,481 |
| Two-part fit, fixed fee ($/month) | 24.03 | 0.56 | [22.94, 25.13] | 18,481 |
| Two-part fit, price ($/kWh) | 0.1034 | 0.0007 | [0.1021, 0.1048] | 18,481 |
| Two-part fit with state effects, price ($/kWh) | 0.1128 | 0.00085 | [0.1111, 0.1144] | 18,481 |
| γ, within-utility class elasticity | −0.0845 | 0.0037 | [−0.0917, −0.0773] | 624 (208 utilities) |
| θ₁, cooperative, equal weights | −0.1120 | 0.0118 | [−0.1352, −0.0888] | 1,018 |
| θ₂, public, equal weights | −0.0191 | 0.0130 | [−0.0445, 0.0063] | 1,018 |
| θ₁, cooperative, customer weights | −0.1262 | 0.0159 | [−0.1573, −0.0951] | 1,018 |
| θ₂, public, customer weights | −0.0472 | 0.0215 | [−0.0894, −0.0050] | 1,018 |

The virtual type rises over the whole 1st–99th percentile range of household use, so the theory's full-sorting
condition (23) holds for this distribution and no bunching is predicted, although the inverse hazard itself stops
falling above the 90th percentile (509 kWh there, 529 kWh at the 99th).

## Reproducing the results

```bash
pip install -r requirements.txt
python src/price_schedules.py
python src/buyers_and_costs.py
```

The first script writes `results/utility_tariffs.csv`, which the second reads. With the committed slim files the
scripts run offline; deleting them makes the scripts download the full public files (about 12 MB and 56 MB).

## Repository layout

| Path | What it is |
|---|---|
| [src/price_schedules.py](src/price_schedules.py) | Tariff selection, tier shapes, bills, names table |
| [src/buyers_and_costs.py](src/buyers_and_costs.py) | Household tests, markup formula, class prices, ownership extension |
| [results/FINDINGS.md](results/FINDINGS.md) | Plain-English summary and every table |
| `results/*.csv`, `results/*.png` | Every number and figure in the README |

## References

- Ito, K. (2014). Do consumers respond to marginal or average price? Evidence from nonlinear electricity pricing.
  *American Economic Review* 104(2), 537–563.
- Maskin, E. & Riley, J. (1984). Monopoly with incomplete information. *RAND Journal of Economics* 15(2), 171–196.
- US Energy Information Administration (2023). *2020 RECS: Using the Microdata File to Compute Estimates and
  Standard Errors*.
