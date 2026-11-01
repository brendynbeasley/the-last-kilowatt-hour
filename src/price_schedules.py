"""Shape of American electricity price schedules, read against Maskin & Riley (1984).

Maskin and Riley show that a seller who cannot tell big buyers from small ones prices later units
more cheaply than earlier ones (Proposition 6), and that only the largest buyer pays marginal cost
for the last unit (Proposition 1). They name utility tariffs as the place where this is "almost
invariably" seen. This script reads every tariff in the OpenEI Utility Rate Database (URDB), keeps
the ones in force today, and asks three things of each:

  1. Does the price of an extra kWh fall, stay flat or rise as monthly use grows (the tier shape)?
  2. What is the bill per kWh, T(q)/q, at fixed monthly use levels, fixed charge included?
  3. Which large, named utilities show which shape?

Tariff shapes are weighted by each utility's 2025 customer count from EIA Form 861. The
utility-level table it writes (results/utility_tariffs.csv) feeds src/buyers_and_costs.py.

Run from the repository root:
    python src/price_schedules.py
The first run downloads the URDB bulk file (about 12 MB) and saves a slim copy in data/raw/.
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

URDB_URL = "https://apps.openei.org/USURDB/download/usurdb.csv.gz"  # OpenEI bulk file, no key
URDB_SLIM = RAW / "usurdb_slim.csv.gz"     # snapshot downloaded 2026-11-01, sectors R/C/I only
EIA861 = RAW / "Sales_Ult_Cust_2025.xlsx"  # EIA-861 2025 final, sales to ultimate customers
TODAY = pd.Timestamp("2026-11-01")         # a tariff is "in force" if not ended before this date
DAYS = 30.42                               # average days per month, for $/day and kWh/day items
N_PERIODS, N_TIERS = 35, 11                # URDB's maximum periods and tiers per tariff
USE_LEVELS = [100, 250, 500, 750, 1000, 1500, 2000, 3000]  # monthly kWh at which bills are priced
SECTORS = ["Residential", "Commercial", "Industrial"]
# Optional and special-purpose tariffs. A standard tariff is any tariff whose name matches none of
# these words; I fixed this list by reading tariff names before computing any shares.
SPECIAL = re.compile(
    r"time.of.use|\btou\b|time.of.day|\btod\b|electric vehicle|\bev\b|net meter|\bnem\b|optional|"
    r"experimental|pilot|employee|light|solar|green|prepa|demand|renewable|interrupt|load control|"
    r"controlled|standby|backup|wind|seasonal|off.peak|peak|critical|smart|\bcpp\b|storage|battery|"
    r"distributed|generation|parallel|cogen|\bdg\b|water heat|dual fuel", re.I)
STALE_DAYS = 730  # drop tariffs last updated over two years before the utility's newest one
# The largest utilities for the names table, by 2025 residential customers; retail marketers and
# utilities with no standard tariff in force in URDB drop out automatically.
N_NAMED = 14
# For the names table only: variants passed over when a plain residential tariff exists.
VARIANT = re.compile(r"with electric space heat|heating|multi|three phase|3.phase|retail access|"
                     r"apartment|rural|non.transmitting|opt.out", re.I)


def load_urdb():
    """Return the slim URDB snapshot, building it from the bulk download on first run."""
    if not URDB_SLIM.exists():
        full = RAW / "usurdb.csv.gz"
        if not full.exists():
            print(f"Downloading {URDB_URL}")
            r = requests.get(URDB_URL, timeout=300)
            r.raise_for_status()
            full.write_bytes(r.content)
        d = pd.read_csv(full, low_memory=False)
        keep = [c for c in d.columns if c in (
            "label", "eiaid", "name", "utility", "sector", "servicetype", "startdate", "enddate",
            "latest_update", "supersedes", "fixedchargefirstmeter", "fixedchargeunits", "mincharge",
            "minchargeunits", "energyweekdayschedule", "flatdemandstructure/period0/tier0rate",
            "demandratestructure/period0/tier0rate")
            or re.match(r"energyratestructure/period\d+/tier\d+(max|rate|adj|unit)$", c)]
        d = d.loc[d.sector.isin(SECTORS), keep]
        d.to_csv(URDB_SLIM, index=False, compression="gzip")
    d = pd.read_csv(URDB_SLIM, low_memory=False).copy()
    print(f"URDB snapshot: {len(d):,} residential, commercial and industrial tariffs, "
          f"{d.eiaid.nunique():,} utilities")
    return d


def tier_table(row, p):
    """List of (upper limit, unit, $/kWh) for period p; the last tier has no upper limit."""
    out = []
    for t in range(N_TIERS):
        rate = row.get(f"energyratestructure/period{p}/tier{t}rate")
        if pd.isna(rate):
            break
        adj = row.get(f"energyratestructure/period{p}/tier{t}adj")
        out.append((row.get(f"energyratestructure/period{p}/tier{t}max"),
                    row.get(f"energyratestructure/period{p}/tier{t}unit"),
                    rate + (0.0 if pd.isna(adj) else adj)))
    return out


def tier_shape(row):
    """Classify how the price of an extra kWh moves across tiers, over all periods."""
    seen = set()
    for p in range(N_PERIODS):
        tiers = tier_table(row, p)
        if not tiers:
            if p == 0:
                return "no energy charge"
            break
        rates = np.array([t[2] for t in tiers])
        step = np.diff(rates)
        if len(rates) < 2 or np.all(np.abs(step) < 1e-9):
            seen.add("flat")
        elif np.all(step <= 1e-9):
            seen.add("declining")
        elif np.all(step >= -1e-9):
            seen.add("increasing")
        else:
            seen.add("mixed")
    seen.discard("flat")
    if not seen:
        return "flat"
    return seen.pop() if len(seen) == 1 else "mixed"


def monthly_periods(row):
    """Period used in each month, or None if periods change within a day (time-of-use)."""
    try:
        sched = json.loads(row["energyweekdayschedule"])
    except (TypeError, ValueError):
        return None
    months = []
    for day in sched:
        if len(set(day)) != 1:
            return None
        months.append(day[0])
    return months if len(months) == 12 else None


def bill(row, q):
    """Average monthly bill ($) and marginal price ($/kWh) at q kWh/month, energy and fixed only.

    Returns (nan, nan) for time-of-use tariffs and for tiers measured per kW of demand."""
    months = monthly_periods(row)
    if months is None:
        return np.nan, np.nan
    fixed = row["fixedchargefirstmeter"]
    fixed = 0.0 if pd.isna(fixed) else fixed * (DAYS if row["fixedchargeunits"] == "$/day" else 1)
    bills, margins = [], []
    for p in months:
        tiers = tier_table(row, p)
        if not tiers:
            return np.nan, np.nan
        energy, lower, marginal = 0.0, 0.0, None
        for i, (upper, unit, rate) in enumerate(tiers):
            if pd.isna(upper) or i == len(tiers) - 1:
                upper = np.inf
            elif unit == "kWh daily":
                upper = upper * DAYS
            elif unit != "kWh":
                return np.nan, np.nan
            energy += rate * max(0.0, min(q, upper) - lower)
            if marginal is None and q < upper:
                marginal = rate  # the tier that the next kWh after q falls in
            lower = upper
        total = energy + fixed
        mn = row["mincharge"]
        if pd.notna(mn) and row["minchargeunits"] == "$/month":
            total = max(total, mn)
        bills.append(total)
        margins.append(marginal)
    return float(np.mean(bills)), float(np.mean(margins))


def customers_2025():
    """Customers by utility number and sector, bundled plus delivery service (EIA-861 2025)."""
    s = pd.read_excel(EIA861, sheet_name="States", header=2, engine="openpyxl")
    cols = list(s.columns)
    s = s[s["Service Type"].isin(["Bundled", "Delivery"])].copy()
    rename = {cols[11]: "Residential", cols[14]: "Commercial", cols[17]: "Industrial"}
    for c in rename:
        s[c] = pd.to_numeric(s[c], errors="coerce")
    s = s.rename(columns=rename).sort_values("Residential", ascending=False)
    g = (s.groupby("Utility Number")
         .agg(utility_name=("Utility Name", "first"), ownership=("Ownership", "first"),
              state=("State", "first"), Residential=("Residential", "sum"),
              Commercial=("Commercial", "sum"), Industrial=("Industrial", "sum")))
    g = g[g.index != 99999]  # EIA's statewide adjustment row, not a utility
    print(f"EIA-861 2025: {len(g):,} bundled or delivery utilities, "
          f"{g.Residential.sum()/1e6:.1f} million residential customers")
    return g


def main():
    d = load_urdb()
    d["end"] = pd.to_datetime(d.enddate, errors="coerce")
    d["start"] = pd.to_datetime(d.startdate, errors="coerce")
    superseded = set(d.supersedes.dropna())
    in_force = d[~d.label.isin(superseded) & (d.end.isna() | (d.end >= TODAY))].copy()
    print(f"In force on {TODAY.date()}: {len(in_force):,} tariffs "
          f"(dropped {len(d) - len(in_force):,} that ended or were superseded)")
    upd = pd.to_datetime(in_force.latest_update, errors="coerce")
    newest = upd.groupby([in_force.eiaid, in_force.sector]).transform("max")
    fresh = in_force[(newest - upd).dt.days <= STALE_DAYS]
    print(f"Dropped {len(in_force) - len(fresh):,} leftovers updated over {STALE_DAYS} days before "
          f"the utility's newest tariff in the same sector; kept {len(fresh):,}")
    std = fresh[~fresh.name.str.contains(SPECIAL, na=False)].copy()
    print(f"Standard tariffs: {len(std):,} (dropped {len(fresh) - len(std):,} optional, "
          f"time-of-use or special-purpose tariffs by name)")
    full_price = std.servicetype.isin(["Bundled", "Delivery with Standard Offer"])
    has_full = full_price.groupby([std.eiaid, std.sector]).transform("any")
    n0 = len(std)
    std = std[full_price | ~has_full].copy()
    print(f"Dropped {n0 - len(std):,} delivery-only tariffs where the same utility lists a "
          f"full-price (bundled or standard-offer) version; kept {len(std):,}")
    std["shape"] = std.apply(tier_shape, axis=1)
    n0 = len(std)
    std = std[std["shape"] != "no energy charge"].copy()
    print(f"Dropped {n0 - len(std):,} tariffs with no energy charge listed; kept {len(std):,}")
    std["fixed_month"] = np.where(std.fixedchargeunits == "$/day",
                                  std.fixedchargefirstmeter * DAYS, std.fixedchargefirstmeter)
    std["has_demand_charge"] = (std["flatdemandstructure/period0/tier0rate"].notna()
                                | std["demandratestructure/period0/tier0rate"].notna())
    std["recent"] = pd.to_datetime(std.latest_update, errors="coerce") >= "2022-01-01"
    for q in USE_LEVELS:
        bm = std.apply(lambda r: bill(r, q), axis=1, result_type="expand")
        std[f"unit_{q}"] = bm[0] / q
        std[f"marg_{q}"] = bm[1]
    shapes = ["declining", "flat", "increasing", "mixed"]
    for s in shapes:
        std[s] = (std["shape"] == s).astype(float)

    # Utility-level averages: each utility's standard tariffs count equally within the utility.
    num = ["declining", "flat", "increasing", "mixed", "fixed_month", "has_demand_charge"] + \
          [f"unit_{q}" for q in USE_LEVELS] + [f"marg_{q}" for q in USE_LEVELS]
    util = std.groupby(["eiaid", "sector"])[num].mean()
    util["n_tariffs"] = std.groupby(["eiaid", "sector"]).size()
    util["all_recent"] = std.groupby(["eiaid", "sector"])["recent"].all()
    util = util.reset_index()
    cust = customers_2025()
    util = util.merge(cust, left_on="eiaid", right_index=True, how="left")
    util["customers"] = [row[row.sector] if pd.notna(row.utility_name) else np.nan
                         for _, row in util.iterrows()]
    unmatched = util.customers.isna() | (util.customers <= 0)
    print(f"Utility-sector cells: {len(util):,}; {unmatched.sum():,} have no 2025 EIA-861 "
          f"customers for that sector and get no weight in customer-weighted shares")
    util.to_csv(OUT / "utility_tariffs.csv", index=False, float_format="%.5f")

    # Table 1: tier shapes by sector, counted three ways.
    rows = []
    w = util[~unmatched]
    for sec in SECTORS:
        t = std[std.sector == sec]
        u = util[util.sector == sec]
        wu = w[w.sector == sec]
        wr = wu[wu.all_recent]
        for basis, frame, wt in [("tariffs", t, None), ("utilities", u, None),
                                 ("customers", wu, "customers"),
                                 ("customers, utilities updated since 2022", wr, "customers")]:
            weights = None if wt is None else frame[wt]
            row = {"sector": sec, "basis": basis, "n": len(frame),
                   "customers_millions": round(frame.customers.sum() / 1e6, 2) if wt else np.nan}
            for s in shapes:
                row[s] = np.average(frame[s], weights=weights)
            rows.append(row)
    shape_tab = pd.DataFrame(rows)
    shape_tab.to_csv(OUT / "tier_shapes.csv", index=False, float_format="%.4f")
    print("\nTier shapes (share of tariffs, utilities or customers):")
    print(shape_tab.round(3).to_string(index=False))

    # Table 2: customer-weighted median unit and marginal price at each use level, residential.
    res = w[(w.sector == "Residential") & w["unit_500"].notna()]
    curve = []
    for q in USE_LEVELS:
        x = res[["customers", f"unit_{q}", f"marg_{q}"]].dropna()
        order = x[f"unit_{q}"].argsort().values
        cum = x.customers.values[order].cumsum() / x.customers.sum()
        med_unit = x[f"unit_{q}"].values[order][np.searchsorted(cum, 0.5)]
        order = x[f"marg_{q}"].argsort().values
        cum = x.customers.values[order].cumsum() / x.customers.sum()
        med_marg = x[f"marg_{q}"].values[order][np.searchsorted(cum, 0.5)]
        curve.append({"kwh_per_month": q, "utilities": len(x),
                      "median_unit_price_cents": 100 * med_unit,
                      "median_marginal_price_cents": 100 * med_marg,
                      "share_unit_price_below_500kwh_level":
                          np.average(x[f"unit_{q}"] < res.loc[x.index, "unit_500"] - 1e-9,
                                     weights=x.customers) if q > 500 else np.nan})
    curve = pd.DataFrame(curve)
    curve.to_csv(OUT / "residential_price_curve.csv", index=False, float_format="%.4f")
    print("\nResidential standard tariffs, customer-weighted medians:")
    print(curve.round(2).to_string(index=False))
    falls = np.average(res["unit_1500"] < res["unit_500"] - 1e-9, weights=res.customers)
    marg_falls = np.average(res["marg_1500"] < res["marg_500"] - 1e-9, weights=res.customers)
    marg_rises = np.average(res["marg_1500"] > res["marg_500"] + 1e-9, weights=res.customers)
    pd.DataFrame([{"utilities": len(res), "customers_millions": res.customers.sum() / 1e6,
                   "share_unit_price_lower_at_1500_than_500": falls,
                   "share_marginal_price_lower_at_1500_than_500": marg_falls,
                   "share_marginal_price_higher_at_1500_than_500": marg_rises,
                   "median_fixed_charge_dollars": res.fixed_month.median()}]
                 ).to_csv(OUT / "residential_discount_summary.csv", index=False, float_format="%.4f")
    print(f"Customer share whose bill per kWh is lower at 1,500 than at 500 kWh: {falls:.3f}; "
          f"marginal price lower: {marg_falls:.3f}; higher: {marg_rises:.3f}")

    # Table 3: the names. One representative standard residential tariff per large utility.
    named = []
    top = cust.sort_values("Residential", ascending=False)
    cand = std[(std.sector == "Residential") & std["unit_500"].notna()].copy()
    cand["plain"] = (~cand.name.str.contains(VARIANT, na=False)).astype(int)
    cand["name_len"] = -cand.name.str.len()
    for uid, info in top.iterrows():
        c = cand[cand.eiaid == uid].sort_values(
            ["plain", "start", "name_len", "label"], ascending=False)
        if c.empty:
            continue
        r = c.iloc[0]
        named.append({"utility": info.utility_name, "state": info.state,
                      "ownership": info.ownership,
                      "residential_customers": int(info.Residential), "tariff": r["name"],
                      "tariff_start": str(r.start.date()) if pd.notna(r.start) else "",
                      "fixed_dollars_month": r.fixed_month, "shape": r["shape"],
                      "marginal_500_cents": 100 * r.marg_500, "marginal_1500_cents": 100 * r.marg_1500,
                      "unit_500_cents": 100 * r.unit_500, "unit_1500_cents": 100 * r.unit_1500})
        if len(named) == N_NAMED:
            break
    named = pd.DataFrame(named)
    named.to_csv(OUT / "named_utilities.csv", index=False, float_format="%.2f")
    print("\nLargest utilities, representative standard residential tariff:")
    print(named.drop(columns=["tariff"]).round(2).to_string(index=False))

    # Figure: bill per kWh and price of the next kWh, residential, by monthly use.
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.plot(curve.kwh_per_month, curve.median_unit_price_cents, "o-", color="#2b6cb0",
            label="Bill per kWh, fixed charge included (median customer)")
    ax.plot(curve.kwh_per_month, curve.median_marginal_price_cents, "s--", color="#c05621",
            label="Price of the next kWh (median customer)")
    ax.set_xscale("log")
    ax.set_xticks(USE_LEVELS)
    ax.set_xticklabels([f"{q:,}" for q in USE_LEVELS])
    ax.set_xlabel("Monthly electricity use (kWh, log scale)")
    ax.set_ylabel("Cents per kWh")
    ax.set_title("Standard residential tariffs in force, November 2026")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "residential_price_curve.png", dpi=150)
    print("\nWrote utility_tariffs.csv, tier_shapes.csv, residential_price_curve.csv/.png, "
          "residential_discount_summary.csv, named_utilities.csv")


if __name__ == "__main__":
    main()
