# Cost model template

Use RMB or the user's requested currency. Keep all rows in the same period and state whether tax, benefits, coordination, and pass-through tools are included.

## Phase comparison

For each role `r`, use the user's named market. If the user asks for a regional benchmark, average cities only when the job level, employment market, period, and data source are comparable. State the reason for the average.

`regional benchmark_r = weighted or simple city average, with the weighting rule stated`

`direct labor_r = monthly benchmark_r × equivalent phase months_r`

`in-house total = Σ direct labor_r × in-house employment coefficient + phase tool fee`

`outsourcing total = Σ direct labor_r × outsourcing service coefficient × coordination factor + phase tool fee`

`tool-only total = necessary operator labor + phase tool fee`

Every coefficient needs a source or an explicit commercial assumption. Use role-specific phase months when senior and junior roles contribute for different durations. Choose the FDE formula from the commercial brief:

- `FDE total = quoted all-in phase price` when the client defines a capped total or the proposal includes project-period trial tools;
- `FDE total = service fee + separately stated pass-through fee` only when the brief explicitly makes tools or subscriptions additional.

Never add an included allowance to the quoted total a second time. If a budget table shows the allowance, label it as an internal allocation or package inclusion rather than an additional client charge.

Label tool-only as non-equivalent when it excludes strategy, role training, evidence governance, integration, QA, or handover.

## Annual scenario

For mixed roles:

`annual released labor = Σ equivalent FTE_r × monthly benchmark_r × employment coefficient_r × 12`

Separate the two periods:

`first-year net cost difference = annual released labor − one-time phase total − first-year operating tool budget`

`later-year run-rate difference = annual released labor − annual operating tool budget − recurring service fee`

Show at least a low, base, and high equivalent-role scenario when the number of released or avoided roles is uncertain. Call the result a budget scenario until operating data validates it. Keep any project-period allowance separate from the post-acceptance annual operating budget, and make clear whether it is included in the quoted phase total. Do not compare a partial-year labor estimate with a full-year tool budget or subtract a one-time phase fee from every later year.

Do not put incremental revenue or GMV into the cost chart. If the user wants it mentioned, write one short note below the chart as an unvalidated upside hypothesis with its measurement method.
