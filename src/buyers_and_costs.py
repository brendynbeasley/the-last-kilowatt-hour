"""What buyers of different sizes actually pay for electricity, and how close the biggest get to cost.

Three tests of Maskin & Riley (1984), plus the ownership extension:

  1. Households (EIA RECS 2020 microdata): does the bill per kWh fall as a household uses more,
     within the same state? And what does the distribution of household use imply for the
     theory's markup formula, p - c = (1 - F) / f, which shrinks to zero at the top?
  2. Customer classes (EIA-861, 2025): average price for residential, commercial and industrial
     customers of the same utility against each utility's own wholesale (sales-for-resale) price,
     the nearest public stand-in for the marginal cost c of a kWh. ICE hub prices are a cross-check.
  3. Ownership: do profit-seeking investor-owned utilities use more quantity discounts than
     customer-owned cooperatives and city-owned utilities? Reads results/utility_tariffs.csv,
     which src/price_schedules.py writes, so run that script first.

Run from the repository root:
    python src/price_schedules.py
    python src/buyers_and_costs.py
The first run downloads the RECS 2020 public file (about 56 MB) and saves a slim copy in data/raw/.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import statsmodels.formula.api as smf
from scipy.stats import gaussian_kde
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

RECS_URL = "https://www.eia.gov/consumption/residential/data/2020/csv/recs2020_public_v7.csv"
RECS_SLIM = RAW / "recs2020_slim.csv.gz"         # DOEID, weights, state, annual kWh and dollars
N_REPLICATES = 60                                # RECS 2020 jackknife replicate weights
JK_COEF = 59 / 60                                # jackknife coefficient, EIA RECS 2020 microdata guide
SALES = RAW / "Sales_Ult_Cust_2025.xlsx"         # EIA-861 2025, sales to ultimate customers
OPS = RAW / "Operational_Data_2025.xlsx"         # EIA-861 2025, sources and disposition
ICE = RAW / "ice_electric-2025final.xlsx"        # EIA wholesale market data, ICE next-day peak trades
PERCENTILES = [10, 25, 50, 75, 90, 95, 99]       # where the markup formula is evaluated
MIN_RESALE_MWH = 10_000  # utilities selling less than this for resale get no wholesale price
# EIA-861 ownership types grouped three ways: profit-seeking, customer-owned, government-owned
OWNER_GROUP = {"Investor Owned": "Investor-owned", "Cooperative": "Cooperative",
               "Municipal": "Public", "Political Subdivision": "Public", "State": "Public",
               "Federal": "Public"}


def load_recs():
    """Slim RECS 2020 household file; built from the public CSV on first run."""
    if not RECS_SLIM.exists():
        full = RAW / "recs2020_public_v7.csv"
        if not full.exists():
            print(f"Downloading {RECS_URL}")
            r = requests.get(RECS_URL, timeout=600)
            r.raise_for_status()
            full.write_bytes(r.content)
        cols = ["DOEID", "NWEIGHT", "state_postal", "KWH", "DOLLAREL"] + \
            [f"NWEIGHT{r}" for r in range(1, N_REPLICATES + 1)]
        pd.read_csv(full, usecols=cols)[cols].round(2).to_csv(RECS_SLIM, index=False,
                                                              compression="gzip")
    d = pd.read_csv(RECS_SLIM)
    n0 = len(d)
    d = d[(d.KWH > 0) & (d.DOLLAREL > 0)].copy()
    print(f"RECS 2020: {n0:,} households, kept {len(d):,} with positive electricity use and "
          f"spending (dropped {n0 - len(d):,})")
    d["kwh_month"] = d.KWH / 12
    d["bill_month"] = d.DOLLAREL / 12
    d["cents"] = 100 * d.DOLLAREL / d.KWH
    return d


def households(d):
    """Bill per kWh by decile of use, the within-state slope, and the two-part fit."""
    d["decile"] = pd.qcut(d.KWH, 10, labels=range(1, 11))
    rows = []
    for k, g in d.groupby("decile", observed=True):
        rows.append({"decile": int(k), "households": len(g),
                     "kwh_per_month": np.average(g.kwh_month, weights=g.NWEIGHT),
                     "bill_per_month": np.average(g.bill_month, weights=g.NWEIGHT),
                     "cents_per_kwh": 100 * (g.DOLLAREL * g.NWEIGHT).sum() / (g.KWH * g.NWEIGHT).sum()})
    dec = pd.DataFrame(rows)
    dec.to_csv(OUT / "household_deciles.csv", index=False, float_format="%.3f")
    print("\nHouseholds by decile of electricity use (RECS 2020, weighted):")
    print(dec.round(2).to_string(index=False))

    # Point estimates use the final weight NWEIGHT. Standard errors come from re-estimating with
    # each of the 60 jackknife replicate weights, as EIA prescribes for RECS 2020.
    specs = [("log price on log use, within state", "np.log(cents) ~ np.log(KWH) + C(state_postal)",
              "np.log(KWH)"),
             ("log price on log use, national", "np.log(cents) ~ np.log(KWH)", "np.log(KWH)"),
             ("monthly bill on monthly kWh, national: intercept ($)", "bill_month ~ kwh_month",
              "Intercept"),
             ("monthly bill on monthly kWh, national: slope ($/kWh)", "bill_month ~ kwh_month",
              "kwh_month"),
             ("monthly bill on monthly kWh, within state: slope ($/kWh)",
              "bill_month ~ kwh_month + C(state_postal)", "kwh_month")]
    rows, fits = [], {}
    for test, formula, term in specs:
        m = smf.wls(formula, d, weights=d.NWEIGHT).fit()
        fits[formula] = m
        X, y, j = m.model.exog, m.model.endog, list(m.params.index).index(term)
        reps = []
        for r in range(1, N_REPLICATES + 1):
            sw = np.sqrt(d[f"NWEIGHT{r}"].values)
            reps.append(np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0][j])
        se = np.sqrt(JK_COEF * np.sum((np.array(reps) - m.params[term]) ** 2))
        rows.append({"test": test, "estimate": m.params[term], "std_error": se,
                     "ci95_low": m.params[term] - 1.96 * se, "ci95_high": m.params[term] + 1.96 * se,
                     "z": m.params[term] / se, "n": int(m.nobs)})
    twopart_nat = fits["bill_month ~ kwh_month"]
    stats = pd.DataFrame(rows)
    stats.to_csv(OUT / "household_tests.csv", index=False, float_format="%.5f")
    print("Standard errors: RECS jackknife, 60 replicate weights")
    print(stats.round(4).to_string(index=False))
    return dec, twopart_nat


def markup_formula(d):
    """Evaluate the inverse hazard (1 - G(q)) / g(q) of monthly household use.

    With vertically parallel linear demand, p(q; v) = v - b q, and today's roughly flat marginal
    price, a household's type is a straight-line function of its use, so the Maskin-Riley markup
    on its last kWh, (1 - F(v)) / f(v), is b times the inverse hazard of use. Dividing by the
    median household's value removes the unknown slope b."""
    x = np.log(d.kwh_month.values)
    kde = gaussian_kde(x, weights=d.NWEIGHT.values)
    grid = np.linspace(np.log(20), np.log(d.kwh_month.max()), 3000)
    dens_log = kde(grid)
    cdf = np.cumsum(dens_log) * (grid[1] - grid[0])
    cdf = cdf / cdf[-1]
    q = np.exp(grid)
    g = dens_log / q                      # density of use in kWh, not log kWh
    inv_hazard = (1 - cdf) / g
    j = q - inv_hazard                    # the "virtual type" must rise with q for full sorting
    w = d.NWEIGHT.values
    order = np.argsort(d.kwh_month.values)
    cumw = np.cumsum(w[order]) / w.sum()
    rows = []
    for pct in PERCENTILES:
        qp = d.kwh_month.values[order][np.searchsorted(cumw, pct / 100)]
        i = np.searchsorted(q, qp)
        rows.append({"percentile": pct, "kwh_per_month": qp, "share_using_more": 1 - cdf[i],
                     "inverse_hazard_kwh": inv_hazard[i]})
    tab = pd.DataFrame(rows)
    tab["markup_relative_to_median"] = tab.inverse_hazard_kwh / \
        tab.loc[tab.percentile == 50, "inverse_hazard_kwh"].iloc[0]
    rising = np.diff(j) > 0
    p_lo = np.searchsorted(q, np.percentile(d.kwh_month, 1))
    p_hi = np.searchsorted(q, np.percentile(d.kwh_month, 99))
    tab.attrs["share_grid_rising"] = rising[p_lo:p_hi].mean()
    tab.to_csv(OUT / "markup_formula.csv", index=False, float_format="%.4f")
    print("\nInverse hazard of monthly household use (the shape of the theory's markup):")
    print(tab.round(3).to_string(index=False))
    print(f"Share of the 1st-99th percentile range where q - (1-G)/g rises: "
          f"{tab.attrs['share_grid_rising']:.3f}")
    pd.DataFrame([{"share_of_p1_p99_range_where_virtual_type_rises": tab.attrs["share_grid_rising"]}]
                 ).to_csv(OUT / "hazard_condition.csv", index=False, float_format="%.4f")
    return tab


def resale():
    """Each utility's 2025 sales for resale (MWh) and revenue from them (thousand dollars)."""
    o = pd.read_excel(OPS, sheet_name="States", header=2, engine="openpyxl")
    for col in ["Sales for Resale", "From Sales for Resale"]:
        o[col] = pd.to_numeric(o[col], errors="coerce")
    o = o.groupby("Utility Number")[["Sales for Resale", "From Sales for Resale"]].sum()
    return o[(o["Sales for Resale"] >= MIN_RESALE_MWH) & (o["From Sales for Resale"] > 0)]


def read_861():
    """Bundled utilities' 2025 revenue, sales and customers by class, plus resale price."""
    s = pd.read_excel(SALES, sheet_name="States", header=2, engine="openpyxl")
    c = list(s.columns)
    s = s[s["Service Type"] == "Bundled"].copy()
    names = {c[9]: "rev_R", c[10]: "mwh_R", c[11]: "cust_R", c[12]: "rev_C", c[13]: "mwh_C",
             c[14]: "cust_C", c[15]: "rev_I", c[16]: "mwh_I", c[17]: "cust_I"}
    s = s.rename(columns=names)
    for col in names.values():
        s[col] = pd.to_numeric(s[col], errors="coerce").fillna(0)
    u = s.groupby("Utility Number").agg(name=("Utility Name", "first"),
                                        ownership=("Ownership", "first"),
                                        **{v: (v, "sum") for v in names.values()})
    u = u[u.index != 99999]
    o = resale()
    u["resale_cents"] = 100 * o["From Sales for Resale"] / o["Sales for Resale"]
    print(f"\nEIA-861 2025: {len(u):,} bundled utilities; {u.resale_cents.notna().sum():,} sell at "
          f"least {MIN_RESALE_MWH:,} MWh for resale and get a wholesale price")
    return u


def customer_classes(u):
    """National class prices, the within-utility comparison and the ICE cross-check."""
    rows = []
    for k, label in [("R", "Residential"), ("C", "Commercial"), ("I", "Industrial")]:
        rows.append({"class": label, "customers": u[f"cust_{k}"].sum(),
                     "kwh_per_customer_month": 1000 * u[f"mwh_{k}"].sum() / u[f"cust_{k}"].sum() / 12,
                     "cents_per_kwh": 100 * u[f"rev_{k}"].sum() / u[f"mwh_{k}"].sum()})
    has = u.resale_cents.notna()
    o = resale()
    rows.append({"class": "Sales for resale (wholesale)", "customers": np.nan,
                 "kwh_per_customer_month": np.nan,
                 "cents_per_kwh": 100 * o["From Sales for Resale"].sum() / o["Sales for Resale"].sum()})
    nat = pd.DataFrame(rows)
    ice = pd.read_excel(ICE, engine="openpyxl")
    ice_avg = ice.groupby("Price hub")["Wtd avg price $/MWh"].mean() / 10
    nat.loc[4] = {"class": "ICE peak trades, average of 7 hubs", "customers": np.nan,
                  "kwh_per_customer_month": np.nan, "cents_per_kwh": ice_avg.mean()}
    nat["markup_over_resale_cents"] = nat.cents_per_kwh - nat.loc[3, "cents_per_kwh"]
    nat.to_csv(OUT / "class_prices.csv", index=False, float_format="%.3f")
    ice_avg.rename("cents_per_kwh").to_csv(OUT / "ice_hubs_2025.csv", float_format="%.3f")
    print("\nNational 2025 prices by customer class, bundled utilities:")
    print(nat.round(2).to_string(index=False))

    # Within utility: same seller, three classes, its own wholesale price.
    full = u[has & (u.cust_R > 0) & (u.cust_C > 0) & (u.cust_I > 0)
             & (u.mwh_R > 0) & (u.mwh_C > 0) & (u.mwh_I > 0)].copy()
    print(f"Within-utility comparison: {len(full):,} utilities with all three classes and a "
          f"wholesale price (dropped {len(u) - len(full):,})")
    long = []
    for k in "RCI":
        full[f"p_{k}"] = 100 * full[f"rev_{k}"] / full[f"mwh_{k}"]
        full[f"q_{k}"] = 1000 * full[f"mwh_{k}"] / full[f"cust_{k}"] / 12
        long.append(pd.DataFrame({"utility": full.index, "cls": k, "price": full[f"p_{k}"],
                                  "kwh": full[f"q_{k}"], "resale": full.resale_cents}))
    long = pd.concat(long)
    fe = smf.ols("np.log(price) ~ np.log(kwh) + C(utility)", long).fit(
        cov_type="cluster", cov_kwds={"groups": long.utility})
    within = pd.DataFrame([{
        "utilities": len(full),
        "median_resale_cents": full.resale_cents.median(),
        **{f"median_price_{k}": full[f"p_{k}"].median() for k in "RCI"},
        **{f"median_gap_{k}_cents": (full[f"p_{k}"] - full.resale_cents).median() for k in "RCI"},
        **{f"share_{k}_within_2c_of_resale": ((full[f"p_{k}"] - full.resale_cents) <= 2).mean()
           for k in "RCI"},
        "share_I_cheapest_class": ((full.p_I < full.p_C) & (full.p_I < full.p_R)).mean(),
        "elasticity_price_wrt_kwh_per_customer": fe.params["np.log(kwh)"],
        "elasticity_se_clustered": fe.bse["np.log(kwh)"],
        "elasticity_ci95_low": fe.conf_int().loc["np.log(kwh)", 0],
        "elasticity_ci95_high": fe.conf_int().loc["np.log(kwh)", 1],
        "elasticity_p_value": fe.pvalues["np.log(kwh)"],
        "observations": int(fe.nobs)}])
    within.to_csv(OUT / "within_utility_classes.csv", index=False, float_format="%.4f")
    print(within.T.round(3).to_string(header=False))
    full.reset_index()[["Utility Number", "name", "ownership", "resale_cents", "p_R", "p_C", "p_I",
                        "q_R", "q_C", "q_I"]].to_csv(OUT / "utility_class_prices.csv", index=False,
                                                     float_format="%.3f")
    return nat, full


def ownership(full):
    """Extension: tariff shapes and class markups by who owns the utility."""
    t = pd.read_csv(OUT / "utility_tariffs.csv")
    t = t[(t.sector == "Residential") & (t.customers > 0)].copy()
    t["group"] = t.ownership.map(OWNER_GROUP)
    t = t[t.group.notna()]
    t["unit_drop"] = (t.unit_1500 < t.unit_500 - 1e-9).astype(float)
    full = full.copy()
    full["group"] = full.ownership.map(OWNER_GROUP)
    t["ratio"] = t.unit_1500 / t.unit_500
    groups = [(grp, g) for grp, g in t.groupby("group")]
    groups.append(("Investor-owned outside California",
                   t[(t.group == "Investor-owned") & (t.state != "CA")]))
    rows = []
    for grp, g in groups:
        gc = g[g.unit_500.notna()]
        fx = g[g.fixed_month.notna()].sort_values("fixed_month")
        cum = fx.customers.cumsum() / fx.customers.sum()
        f = full[full.group == grp] if grp in OWNER_GROUP.values() else full.iloc[0:0]
        rows.append({
            "owner": grp, "utilities": len(g), "residential_customers_millions": g.customers.sum() / 1e6,
            **{s: np.average(g[s], weights=g.customers) for s in
               ["declining", "flat", "increasing", "mixed"]},
            "median_fixed_charge_dollars": fx.fixed_month.values[np.searchsorted(cum, 0.5)],
            "unit_price_ratio_1500_to_500": np.average(gc.unit_1500 / gc.unit_500, weights=gc.customers),
            "share_unit_price_falls_500_to_1500": np.average(gc.unit_drop, weights=gc.customers),
            "utilities_with_class_prices": len(f),
            "median_residential_gap_cents": (f.p_R - f.resale_cents).median(),
            "median_industrial_gap_cents": (f.p_I - f.resale_cents).median()})
    tab = pd.DataFrame(rows)
    tab.to_csv(OUT / "ownership.csv", index=False, float_format="%.4f")
    print("\nExtension, residential tariffs and class gaps by ownership (customer-weighted):")
    print(tab.round(3).T.to_string(header=False))

    # Is the cooperative / public difference in the 1,500-to-500 kWh price ratio more than noise?
    r = t[t.ratio.notna()].copy()
    r["coop"] = (r.group == "Cooperative").astype(int)
    r["public"] = (r.group == "Public").astype(int)
    tests = []
    for label, wts in [("utilities weighted equally", None), ("weighted by customers", r.customers)]:
        m = (smf.ols("ratio ~ coop + public", r) if wts is None else
             smf.wls("ratio ~ coop + public", r, weights=wts)).fit(cov_type="HC1")
        for term in ["Intercept", "coop", "public"]:
            lo, hi = m.conf_int().loc[term]
            tests.append({"weights": label, "term": term, "estimate": m.params[term],
                          "std_error": m.bse[term], "ci95_low": lo, "ci95_high": hi,
                          "p_value": m.pvalues[term], "n": int(m.nobs)})
    tests = pd.DataFrame(tests)
    tests.to_csv(OUT / "ownership_tests.csv", index=False, float_format="%.5f")
    print("\nBill per kWh at 1,500 kWh divided by bill per kWh at 500 kWh, on ownership "
          "(investor-owned is the base):")
    print(tests.round(4).to_string(index=False))
    return tab


def figures(dec, fit, full, nat):
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.plot(dec.kwh_per_month, dec.cents_per_kwh, "o", color="#2b6cb0", ms=7,
            label="Households, by decile of use (RECS 2020)")
    q = np.linspace(dec.kwh_per_month.min(), dec.kwh_per_month.max(), 200)
    a, b = fit.params["Intercept"], fit.params["kwh_month"]
    ax.plot(q, 100 * (a + b * q) / q, "-", color="#718096",
            label=f"Fixed ${a:.0f} a month plus {100*b:.1f}¢ per kWh")
    ax.set_xlabel("Average monthly electricity use (kWh)")
    ax.set_ylabel("Bill per kWh (cents)")
    ax.set_title("Bigger households pay less per kWh")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "household_unit_prices.png", dpi=150)

    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    colors = {"R": "#2b6cb0", "C": "#2f855a", "I": "#c05621"}
    labels = {"R": "Residential", "C": "Commercial", "I": "Industrial"}
    for k in "RCI":
        ax.scatter(full[f"q_{k}"], full[f"p_{k}"] - full.resale_cents, s=8, alpha=0.25,
                   color=colors[k], label=f"{labels[k]} (one dot per utility)")
    for i, k in enumerate("RCI"):
        ax.scatter(nat.loc[i, "kwh_per_customer_month"], nat.loc[i, "markup_over_resale_cents"],
                   s=120, marker="D", color=colors[k], edgecolor="black", zorder=5)
    ax.axhline(0, color="black", lw=1)
    ax.set_xscale("log")
    ax.set_ylim(-10, 30)
    ax.set_xlabel("Monthly use per customer (kWh, log scale)")
    ax.set_ylabel("Average price minus wholesale price (cents/kWh)")
    ax.set_title("The biggest buyers pay closest to wholesale (2025)")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "price_by_class.png", dpi=150)


def main():
    d = load_recs()
    dec, fit = households(d)
    markup_formula(d)
    u = read_861()
    nat, full = customer_classes(u)
    ownership(full)
    figures(dec, fit, full, nat)
    print("\nWrote household_*.csv, markup_formula.csv, hazard_condition.csv, class_prices.csv, "
          "ice_hubs_2025.csv, within_utility_classes.csv, utility_class_prices.csv, ownership.csv "
          "and two figures")


if __name__ == "__main__":
    main()
