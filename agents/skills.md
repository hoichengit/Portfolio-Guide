# Agent skills

**Purpose:** Give each role a specific financial problem, an observable output and a check.

| Skill area | Why it exists | Evidence |
|---|---|---|
| [Financial mapping](#financial) | Prevent mismatched periods, units and definitions. | Original report → Excel. |
| [Research translation](#research) | Connect external information to a model assumption. | Source → driver implication. |
| [Scenario design](#scenario) | Make uncertainty explicit and cases internally consistent. | Assumptions → calculated results. |
| [QA review](#qa) | Expose errors rather than hide them. | Finding → correction or retained limitation. |
| [Business drivers](#business_driver) | Explain change rather than repeat totals. | Revenue / segment / margin bridges. |

<a id="financial"></a>
## Financial mapping

**Problem:** Different year orders or definitions can create a false comparison.

Preserve fiscal dates, source rows, units and signs. Label reported amounts and derived metrics separately. [Expand the revenue example](financial.md#worked-example).

<a id="research"></a>
## Research translation

**Problem:** General economic news does not automatically quantify a company forecast.

Record publication dates, source evidence, direction and the affected input. Explain timing and overlap before changing assumptions. [Inspect the cost example](research.md#worked-example).

<a id="scenario"></a>
## Scenario design

**Problem:** A plausible narrative can still produce inconsistent financial assumptions.

Specify complete bear/base/bull inputs, use matched history and preserve the original forecasts. Excel and Python calculate the consequences. [Inspect the scenarios](scenario.md#worked-example).

<a id="qa"></a>
## QA review

**Problem:** A tidy dashboard can conceal a wrong input or a leaked future result.

Check date eligibility, units, formula results and source reconciliation. Preserve failures and rounding differences. [Inspect the reconciliation example](qa.md#worked-example).

<a id="business_driver"></a>
## Business drivers

**Problem:** Total growth does not reveal its source or sustainability.

Separate volume, price, FX, segment contribution and margin effects. Keep rounded narrative contributions distinct from exact arithmetic. [Inspect Beauty's contribution](business_driver.md#worked-example).

[← All agents](README.md) · [Project home](../README.md)
