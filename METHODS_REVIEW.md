# Methods review: Maskin and Riley (1984)

- **Paper.** Eric Maskin and John Riley, "Monopoly with Incomplete Information," *RAND Journal of Economics*
  15(2), Summer 1984, pp. 171–196. Author affiliations as printed: Massachusetts Institute of Technology (Maskin)
  and University of California, Los Angeles (Riley).
- **Statistical focus.** The characterization of the profit-maximizing nonlinear price schedule, in particular
  Proposition 1 (demand price exceeds marginal cost for every type except the highest) and Proposition 6 (the
  unit price T(q)/q declines everywhere under condition (30)), together with the paper's one empirical claim, on
  p. 184, that utility multipart tariffs "almost invariably" offer lower unit prices for greater consumption.
- **Review standard.** For a theory paper, internal consistency of the formal results, how explicitly the
  assumptions are stated, and whether the predictions can be tested with observable data. Data and code
  availability standards do not apply because the paper uses no data.
- **What was read.** The full published text, from the JSTOR scan linked on Eric Maskin's Harvard faculty page,
  retrieved through an Internet Archive snapshot dated June 16, 2025, and converted to text. The figures and several
  displayed equations did not survive text extraction, so equation-level details are reported only where the
  surrounding prose states them, and garbled items are flagged below. Nothing here is taken from secondary summaries.

## Methods summary

The paper is a mathematical derivation, not an empirical study. A monopolist produces at constant marginal cost c
and sells to buyers whose preferences are indexed by one parameter v, drawn from a distribution F the seller knows
but whose realization it cannot see. Utility is quasi-linear, the integral of a demand price p(x; v) up to the
quantity bought minus the payment, so there are no income effects (eq. 1 and footnote 2). The seller offers a
schedule of quantity-payment pairs and each buyer picks one, with buying nothing always available.

Section 2 gives a two-type diagram and Proposition 1. Section 3 shows, first for finitely many types, that only the
"local downward" self-selection constraints bind (eq. 11), that quantity is nondecreasing in type (eq. 8) and that
the lowest type gets no surplus (eq. 12), then passes to a continuum. Integration by parts turns expected profit
into the expectation of I(q; v) = N(q; v) − N_v(q; v)/ρ(v), where N is the surplus of the sale and ρ = f/(1 − F) is
the hazard rate (Proposition 2, eq. 17). Proposition 3 gives the payment schedule T(q) = ∫ p(z; φ(z)) dz (eq. 19).
Section 4 gives conditions for complete sorting (Proposition 4, conditions 23 and 24), two closed-form examples,
a comparative static in the distribution (Proposition 5), the quantity-discount result (Proposition 6) and the
general characterization with bunching intervals (Proposition 7, proved in the appendix). Section 5 extends the
method to quality and bundling (Proposition 8, Example 3). Section 6 discusses the role of the two key
assumptions and an application to principal-agent contracting.

## Research design

A deductive model. The "design" is the set of assumptions: quasi-linear utility and risk neutrality toward income
(Section 6), a single taste parameter, demand prices increasing in v (Assumption 1), a continuous strictly
increasing F on (0, v̄] (Assumption 2), demand elasticity nondecreasing in the demand price (Assumption 3, eq. 20),
p_vv < 0 as a normalization (Assumption 4), and, for Proposition 7, strict quasi-concavity of I and a single-crossing
condition (Assumptions 5 and 6). The assumptions are stated explicitly and numbered, and the text says which
proposition uses which.

## Sampling strategy

Does not apply. There is no sample. F is interpreted either as the distribution from which buyers are drawn or as
the realized distribution of buyers (footnote 3).

## Sample size

Does not apply.

## Inclusion and exclusion criteria

Does not apply as a data matter. The model excludes, by assumption, income effects, buyer risk aversion over
income, multi-dimensional tastes, selling schemes in which one buyer's terms depend on others' choices, and random
schedules (footnote 4). Random schemes are argued not to help under Assumption 3, with the proof deferred to Maskin
and Riley (1983a).

## Independent and dependent variables

In the model, the type v is the primitive and the quantity schedule q*(v), the payment schedule T(q) and the
markup p(q*(v); v) − c are the outcomes. Comparative statics are with respect to the distribution F (Proposition 5).

## Statistical methods

Does not apply in the statistical sense. The analytical methods are a self-selection (incentive-compatibility)
argument, integration by parts to obtain virtual surplus, pointwise maximization under a monotonicity constraint
and, where pointwise maximization fails, a variational argument that produces bunching intervals.

## Reported effect sizes

There are no estimated effects. The closest analogues are the closed-form solutions. In Example 1 (vertically
parallel demand p = v − h(q)), φ(v) = h⁻¹(max{0, J(v) − c}) with J(v) = v − (1 − F(v))/F′(v), which implies a
marginal-price markup of (1 − F)/f at each purchased quantity. Footnote 9 gives a distribution, F(v) = v(7 − 9v +
4v²)/2, for which J(1/2) = J(5/8) = J(3/4) > 0, showing that J need not be monotone. By direct substitution the
common value is 1/4.

## Confidence intervals

Does not apply; no estimates are reported.

## P-values, if applicable

Does not apply.

## Missing data treatment

Does not apply. Two pieces of the formal argument are not in the paper itself. The rigorous limit from the finite
to the continuous case is deferred to Maskin and Riley (1983b), and the ruling out of random schemes to Maskin and
Riley (1983a). The proofs of Propositions 5 and 6 are given only for the case where pointwise maximization is
monotone, with the general case said to follow from Proposition 7.

## Stated limitations

The authors name two assumptions as crucial in Section 6: no income effects with neutrality toward income risk,
and a one-parameter family of demand curves, noting that extending to even two parameters "will not be easy." They
also note that the seller is assumed to hold all bargaining power, and that quantity premiums may be hard to enforce
because buyers can split purchases (p. 184 and footnote 10), while discounts can be undone by bulk-buying
coalitions.

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Inefficiency at all but the top | p(q(v_i); v_i) ≥ c for all i, strict for i < n | Proposition 1, p. 175 | Every type but the highest buys less than the efficient quantity | How large the distortion is, or that real sellers price this way |
| Expected profit as virtual surplus | E[profit] = ∫ I(q(v); v) dF, I = N − N_v/ρ, ρ = f/(1 − F) | Proposition 2, eq. (17), p. 180 | Reduces the screening problem to a pointwise maximization | Results for multi-dimensional types or with income effects |
| Optimal payment schedule | T(q) = ∫₀^q p(z; φ(z)) dz | Proposition 3, eq. (19), p. 181 | The tariff that implements the optimal quantities | A fixed fee; the schedule as written starts at T(0) = 0 |
| Complete-sorting condition | J(v) = v − (1 − F(v))/F′(v) increasing (eq. 23), or eq. (24) | Proposition 4, pp. 182–183 | When no two types are bunched | That common distributions satisfy it in the relevant range |
| Example 1 solution | φ(v) = h⁻¹(max{0, J(v) − c}) | p. 183 | Closed-form quantities; implies markup (1 − F)/f | Magnitudes for any real market |
| Non-monotone J example | F(v) = v(7 − 9v + 4v²)/2 gives J(1/2) = J(5/8) = J(3/4) > 0 | Footnote 9, p. 183 | That the regularity condition can fail with a smooth F | How often it fails in practice |
| Distribution shift | Lower hazard rate everywhere implies a strictly steeper T(q) | Proposition 5, p. 184 | Comparative static for a "more favorable" buyer population | That any rightward shift raises the whole schedule (Figure 4 shows it need not) |
| Quantity discounts | T(q)/q declining everywhere under condition (30) | Proposition 6, pp. 185–186 | Unit price falls with quantity; sufficient conditions are Assumption 3, a nondecreasing hazard and p_qv < 0 | That marginal prices fall, except through the proof's intermediate step |
| Bunching | q*(v) constant on intervals [x_i, y_i] where pointwise maxima fall; never discontinuous under Assumptions 1, 2, 3 | Proposition 7, p. 187, appendix | Shape of the optimum when J is not monotone | Where the intervals lie in any real distribution |
| Bundling example | B = 2vqz^(1/2) − q³/3, F(v) = v; quantity sold rises with quality along the schedule | Example 3, eqs. (36)–(38), p. 190 | A solved case of quality-quantity bundling | The printed closed form could not be read reliably from the scan |
| Empirical claim | Utility multipart tariffs "almost invariably" offer lower unit prices for greater consumption | Section 4, p. 184 | The authors' motivation from observed pricing | Any measurement; no source or count is given |

## Interpretation notes

- **Reporting matters, not errors.** The paper reports no data, so the usual reporting concerns (standard errors,
  sample construction) do not arise. The one empirical sentence on p. 184 is offered without a source, which is a
  reporting gap rather than an analytical error. The IDEAS record for the paper lists no correction, and I am not
  aware of a published comment documenting an error in the formal results.
- **Unit price versus marginal price.** Proposition 6 is stated for the average payment per unit, T(q)/q. A two-part
  tariff with a fixed fee and constant marginal price also has declining T(q)/q, so observing declining unit prices
  does not by itself distinguish the paper's screening schedule from simple fixed-cost recovery. The sharper
  implication, that the marginal price p(q*(v); v) falls with v toward c, appears in the proof of Proposition 6
  rather than as a headline statement.
- **No distortion at the top refers to one type.** Proposition 1 leaves the markup at zero only for the highest
  type. With a long right tail the markup for buyers near, but below, the top can remain large.
- **Seller power.** The seller is an unregulated monopolist with full commitment. The authors flag in Section 6 that
  outcomes elsewhere on the Pareto frontier may emerge under negotiation.

## Unanswered questions

- How sensitive are the qualitative results, especially Proposition 6, to the one-dimensional type assumption that
  the authors call crucial?
- What happens with a fixed per-customer cost, which footnote 7 says the method can handle but the paper does not
  solve?
- How large are the predicted markups and welfare losses for plausible demand curves and distributions? The paper
  gives no calibrated example.
- What evidence supports the "almost invariably" claim about utility tariffs in 1984, and was it about unit prices
  or marginal prices?

## Items requiring expert verification

- The exact printed forms of equations (24), (30) and Example 3's closed form (eqs. 36–38 and the final bundling
  schedule), which were partly garbled in text extraction.
- Whether footnote 7's modified boundary condition is printed as U*(0) = k or with a different sign convention.
- The status of the deferred proofs in Maskin and Riley (1983a, 1983b), which the paper cites as working papers.

## How the modern rerun relates

This repository does not reproduce the paper, which has nothing empirical to reproduce. It takes the paper's two
testable implications to present-day US electricity prices. Unit prices that fall with use, the form Proposition 6
states, are found for 87% of residential customers. Marginal prices that fall with use, the sharper implication, are
not typical: weighted by customers, 12.8% of residential customers face declining blocks and 34.4% inclining ones.
Electric utilities are regulated or customer-owned, so these results speak to whether real tariffs look like the
paper's schedule, not to whether the paper's derivations are correct.
