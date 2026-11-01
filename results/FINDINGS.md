# Maskin & Riley (1984) on 2026 electricity tariffs: findings

## In plain English

Maskin and Riley showed that a seller who cannot tell big buyers from small ones should charge less per unit for
larger purchases, by making each extra unit cheaper, and should charge the very largest buyer only cost for its
last unit. They said utility tariffs almost always looked like this. I checked US electricity prices in 2025 and
2026.

- **Bigger buyers do pay less per kilowatt-hour.** The heaviest tenth of American households pays 11.3 cents per
  kWh against 18.7 cents for the lightest tenth, and 87% of residential customers are on a standard tariff that is
  cheaper per kWh at 1,500 kWh a month than at 500. Commonwealth Edison, Florida Power & Light, Georgia Power and
  PECO all work this way.
- **But the discount comes from the fixed monthly charge, not from cheaper extra power.** Only 12.8% of residential
  customers face declining blocks; 34.4% face inclining blocks, under which extra kilowatt-hours cost more, as at
  Florida Power & Light, Georgia Power and Pacific Gas & Electric. Of the fourteen largest residential utilities, only
  Duke Energy Carolinas has declining blocks.
- **The largest customers come closest to paying cost.** Industrial customers pay 2.30 cents above the wholesale
  price on average, households 10.90 cents. At 90% of utilities that report all three classes, industrial customers
  pay the lowest price.
- **Customer-owned cooperatives discount more steeply than investor-owned companies.** Co-op members save about 20%
  per kWh going from 500 to 1,500 kWh a month, investor-owned customers about 7.5%. That points to cost recovery
  rather than profit-driven screening.

A longer tour is in the [README](../README.md). The rest of this page is every table the scripts produce.

**Key to the labels.** *Declining / flat / increasing (inclining) / mixed* describe how the energy rate moves
across a tariff's usage tiers; *mixed* means a period's tiers both rise and fall, or seasons or periods disagree. *Unit price* is the bill per kWh,
T(q)/q, fixed charge included. *Marginal price* is the rate on the tier the next kWh falls into. *Resale price* is a
utility's revenue from sales for resale divided by its MWh sold for resale. *R, C, I* are residential, commercial,
industrial. Shares are fractions (0.128 = 12.8%). Prices are cents per kWh unless marked.

## Tier shapes of standard tariffs in force (`tier_shapes.csv`)

Counted by tariff, by utility (each utility's tariffs averaged), and by customer (utilities weighted by 2025 EIA-861
customers). The last row of each sector keeps only utilities all of whose standard tariffs were updated since 2022.

| Sector | Basis | n | Customers (millions) | Declining | Flat | Increasing | Mixed |
|---|---|---|---|---|---|---|---|
| Residential | tariffs | 4,268 | | 0.273 | 0.523 | 0.119 | 0.086 |
| Residential | utilities | 2,513 | | 0.270 | 0.541 | 0.108 | 0.081 |
| Residential | customers | 1,023 | 118.58 | 0.128 | 0.465 | 0.344 | 0.063 |
| Residential | customers, updated since 2022 | 167 | 97.70 | 0.116 | 0.433 | 0.387 | 0.063 |
| Commercial | tariffs | 8,240 | | 0.323 | 0.622 | 0.022 | 0.033 |
| Commercial | utilities | 2,522 | | 0.322 | 0.604 | 0.027 | 0.046 |
| Commercial | customers | 1,021 | 15.40 | 0.240 | 0.722 | 0.019 | 0.019 |
| Commercial | customers, updated since 2022 | 106 | 11.84 | 0.213 | 0.747 | 0.020 | 0.019 |
| Industrial | tariffs | 2,936 | | 0.254 | 0.725 | 0.011 | 0.010 |
| Industrial | utilities | 1,304 | | 0.268 | 0.705 | 0.014 | 0.012 |
| Industrial | customers | 618 | 0.41 | 0.289 | 0.695 | 0.009 | 0.007 |
| Industrial | customers, updated since 2022 | 67 | 0.21 | 0.211 | 0.768 | 0.011 | 0.011 |

Small utilities dominate the tariff and utility counts, and they use declining blocks more often than the large
utilities that dominate the customer counts.

## Residential unit and marginal prices by monthly use (`residential_price_curve.csv`)

Customer-weighted medians across 1,018 utilities with a priceable standard residential tariff. The last column is
the customer share whose unit price at that level is below its unit price at 500 kWh.

| kWh per month | Median unit price | Median marginal price | Share with unit price below the 500 kWh level |
|---|---|---|---|
| 100 | 30.05 | 13.83 | |
| 250 | 20.68 | 13.83 | |
| 500 | 17.46 | 13.83 | |
| 750 | 16.24 | 14.15 | 0.915 |
| 1,000 | 15.99 | 14.87 | 0.872 |
| 1,500 | 15.45 | 14.87 | 0.871 |
| 2,000 | 15.27 | 14.92 | 0.871 |
| 3,000 | 15.01 | 14.92 | 0.871 |

## Residential discount summary (`residential_discount_summary.csv`)

| Utilities | Customers (millions) | Unit price lower at 1,500 than 500 | Marginal price lower at 1,500 | Marginal price higher at 1,500 | Median fixed charge |
|---|---|---|---|---|---|
| 1,018 | 118.37 | 0.871 | 0.190 | 0.299 | $14.75 |

## The fourteen largest residential utilities (`named_utilities.csv`)

One representative standard residential tariff each: a plain residential tariff where one exists, newest start
date first. The CSV also lists each tariff's name.

| Utility | State | Customers | Tariff start | Fixed $/month | Shape | Marginal at 500 | Marginal at 1,500 | Unit at 500 | Unit at 1,500 |
|---|---|---|---|---|---|---|---|---|---|
| Florida Power & Light | FL | 5,337,118 | 2026-01-01 | 10.52 | increasing | 12.26 | 14.26 | 14.36 | 13.63 |
| Pacific Gas & Electric | CA | 5,055,556 | 2026-03-27 | 24.14 | increasing | 40.70 | 40.70 | 41.98 | 41.13 |
| Southern California Edison | CA | 4,627,247 | 2024-06-01 | 0.94 | increasing | 39.98 | 43.18 | 35.50 | 40.59 |
| Commonwealth Edison | IL | 3,753,924 | 2025-01-01 | 19.52 | flat | 12.64 | 12.64 | 16.54 | 13.94 |
| Consolidated Edison | NY | 3,088,999 | 2025-02-01 | 20.00 | increasing | 37.64 | 37.64 | 41.24 | 38.84 |
| Duke Energy Carolinas | NC | 2,543,170 | 2026-02-01 | 11.78 | declining | 15.15 | 14.57 | 17.51 | 15.67 |
| Virginia Electric & Power (Dominion) | VA | 2,517,958 | 2026-01-01 | 7.58 | mixed | 16.28 | 15.36 | 17.79 | 16.36 |
| Georgia Power | GA | 2,480,484 | 2025-01-01 | 14.00 | increasing | 13.83 | 16.20 | 16.63 | 16.06 |
| DTE Electric | MI | 2,078,328 | 2026-04-01 | 9.75 | increasing | 22.82 | 22.82 | 24.73 | 23.46 |
| Public Service Electric & Gas | NJ | 2,072,339 | 2026-04-01 | 6.00 | increasing | 26.94 | 27.39 | 28.14 | 27.61 |
| PacifiCorp | UT | 1,867,246 | 2026-01-01 | 24.24 | flat | 12.18 | 12.18 | 17.02 | 13.79 |
| Duke Energy Florida | FL | 1,819,962 | 2026-02-01 | 14.27 | increasing | 13.77 | 15.78 | 16.62 | 15.39 |
| Consumers Energy | MI | 1,662,741 | 2025-01-01 | 8.73 | increasing | 22.84 | 24.62 | 24.58 | 24.49 |
| PECO | PA | 1,538,993 | 2026-01-01 | 11.30 | flat | 21.88 | 21.88 | 24.14 | 22.64 |

Some tariffs have an inclining tier below 500 kWh or in summer only, so the shape can be "increasing" while the two
marginal prices shown are equal. Southern California Edison is the one large utility whose unit price rises between
500 and 1,500 kWh.

## Households by decile of electricity use (`household_deciles.csv`)

RECS 2020, weighted by NWEIGHT.

| Decile | Households | kWh per month | Bill per month | Cents per kWh |
|---|---|---|---|---|
| 1 | 1,849 | 216.0 | $40.37 | 18.69 |
| 2 | 1,848 | 375.3 | $62.04 | 16.53 |
| 3 | 1,848 | 492.5 | $76.27 | 15.49 |
| 4 | 1,848 | 603.3 | $89.08 | 14.77 |
| 5 | 1,848 | 717.2 | $99.13 | 13.82 |
| 6 | 1,848 | 841.8 | $113.14 | 13.44 |
| 7 | 1,848 | 989.2 | $129.19 | 13.06 |
| 8 | 1,848 | 1,176.6 | $146.98 | 12.49 |
| 9 | 1,848 | 1,453.3 | $174.34 | 12.00 |
| 10 | 1,848 | 2,165.4 | $244.97 | 11.31 |

## Household regressions (`household_tests.csv`)

Weighted least squares with NWEIGHT; standard errors from the 60 RECS jackknife replicate weights.

| Test | Estimate | SE | 95% CI | z | N |
|---|---|---|---|---|---|
| Log price on log use, state fixed effects | −0.1384 | 0.0051 | [−0.1483, −0.1284] | −27.4 | 18,481 |
| Log price on log use, national | −0.2122 | 0.0049 | [−0.2218, −0.2027] | −43.4 | 18,481 |
| Monthly bill on monthly kWh, intercept ($) | 24.03 | 0.56 | [22.94, 25.13] | 43.0 | 18,481 |
| Monthly bill on monthly kWh, slope ($/kWh) | 0.1034 | 0.0007 | [0.1021, 0.1048] | 150.5 | 18,481 |
| Same slope with state fixed effects ($/kWh) | 0.1128 | 0.00085 | [0.1111, 0.1144] | 132.9 | 18,481 |

## The markup formula on household use (`markup_formula.csv`, `hazard_condition.csv`)

Inverse hazard (1 − G(q))/g(q) of monthly household use from a weighted kernel density. Under vertically parallel
linear demand and a flat current marginal price, the Maskin-Riley markup on a household's last kWh is proportional
to it.

| Percentile | kWh per month | Share using more | Inverse hazard (kWh) | Markup relative to median |
|---|---|---|---|---|
| 10 | 289 | 0.899 | 1,231 | 1.931 |
| 25 | 468 | 0.746 | 830 | 1.302 |
| 50 | 754 | 0.498 | 638 | 1.000 |
| 75 | 1,151 | 0.253 | 550 | 0.862 |
| 90 | 1,625 | 0.103 | 509 | 0.798 |
| 95 | 1,969 | 0.052 | 512 | 0.803 |
| 99 | 2,777 | 0.011 | 529 | 0.829 |

The virtual type q − (1 − G)/g rises over 100% of the 1st–99th percentile range, so the full-sorting condition
holds and the theory predicts no bunching for this distribution.

## Prices by customer class, 2025 (`class_prices.csv`, `ice_hubs_2025.csv`)

Bundled utilities, EIA-861 2025. The last column subtracts the national resale price, which pools every Form 861
filer with at least 10,000 MWh of sales for resale. The ICE row averages 2025 next-day peak trades at seven hubs, two
of them real-time products.

| Class | Customers | kWh per customer per month | Cents per kWh | Above resale price |
|---|---|---|---|---|
| Residential | 127,498,553 | 890 | 16.61 | 10.90 |
| Commercial | 16,337,978 | 5,960 | 12.37 | 6.65 |
| Industrial | 989,731 | 70,268 | 8.01 | 2.30 |
| Sales for resale (wholesale) | | | 5.72 | 0 |
| ICE peak trades, average of 7 hubs | | | 5.16 | −0.56 |

| ICE hub, 2025 peak | Cents per kWh |
|---|---|
| Indiana Hub RT Peak | 7.08 |
| Mid C Peak | 4.62 |
| NP15 EZ Gen DA LMP Peak | 4.24 |
| Nepool MH DA LMP Peak | 7.79 |
| PJM WH Real Time Peak | 6.02 |
| Palo Verde Peak | 3.52 |
| SP15 EZ Gen DA LMP Peak | 2.87 |

## Within-utility class comparison (`within_utility_classes.csv`, `utility_class_prices.csv`)

208 bundled utilities with all three classes and at least 10,000 MWh of resale. The per-utility prices are in
`utility_class_prices.csv`.

| Statistic | Value |
|---|---|
| Median resale price | 5.33 |
| Median price, R / C / I | 14.64 / 12.44 / 8.90 |
| Median gap above own resale price, R / C / I | 9.50 / 7.02 / 3.73 |
| Share within 2 cents of own resale price, R / C / I | 0.096 / 0.149 / 0.337 |
| Share where industrial is the cheapest class | 0.899 |
| Elasticity of price with respect to kWh per customer, utility fixed effects | −0.0845 (SE 0.0037, clustered by utility) |
| 95% CI | [−0.0917, −0.0773] |
| Observations | 624 |

## Extension: ownership (`ownership.csv`, `ownership_tests.csv`)

Residential standard tariffs, customer-weighted; class gaps are medians over utilities with all three classes and a
resale price.

| Owner | Utilities | Customers (millions) | Declining | Flat | Increasing | Mixed | Median fixed charge | Unit price 1,500 ÷ 500 | Share whose unit price falls | Utilities with class prices | Median R gap | Median I gap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cooperative | 437 | 14.78 | 0.183 | 0.635 | 0.092 | 0.091 | $20.56 | 0.799 | 0.990 | 29 | 7.38 | 1.66 |
| Investor-owned | 120 | 87.24 | 0.119 | 0.435 | 0.389 | 0.056 | $13.69 | 0.925 | 0.853 | 100 | 11.21 | 4.08 |
| Public | 466 | 16.55 | 0.123 | 0.471 | 0.331 | 0.075 | $15.00 | 0.878 | 0.861 | 78 | 7.17 | 3.31 |
| Investor-owned outside California | 116 | 76.16 | 0.137 | 0.498 | 0.300 | 0.065 | $13.50 | 0.904 | 0.977 | | | |

Regression of the unit-price ratio on ownership dummies (investor-owned is the base), HC1 errors:

| Weights | Term | Estimate | SE | 95% CI | p | N |
|---|---|---|---|---|---|---|
| Equal | Intercept | 0.907 | 0.010 | [0.887, 0.927] | < 0.001 | 1,018 |
| Equal | Cooperative | −0.112 | 0.012 | [−0.135, −0.089] | < 0.001 | 1,018 |
| Equal | Public | −0.019 | 0.013 | [−0.044, 0.006] | 0.140 | 1,018 |
| Customers | Intercept | 0.925 | 0.015 | [0.896, 0.954] | < 0.001 | 1,018 |
| Customers | Cooperative | −0.126 | 0.016 | [−0.157, −0.095] | < 0.001 | 1,018 |
| Customers | Public | −0.047 | 0.022 | [−0.089, −0.005] | 0.028 | 1,018 |

## Figures

- `residential_price_curve.png`: median unit price and marginal price by monthly use, residential.
- `household_unit_prices.png`: RECS deciles with the fitted fixed-fee-plus-flat-rate curve.
- `price_by_class.png`: each utility's class price minus its own resale price against use per customer.

The utility-level tariff file behind the tier shapes and the ownership extension is `utility_tariffs.csv`.
