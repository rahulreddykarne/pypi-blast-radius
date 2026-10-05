<div align="center">

# pypi-blast-radius

**Estimate the downstream impact (“blast radius”) of a PyPI package version from deps.dev dependents and download volume.**

[![PyPI](https://img.shields.io/pypi/v/pypi-blast-radius?color=blue)](https://pypi.org/project/pypi-blast-radius/)
[![Python](https://img.shields.io/pypi/pyversions/pypi-blast-radius)](https://pypi.org/project/pypi-blast-radius/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/pypi-blast-radius/month)](https://pepy.tech/project/pypi-blast-radius)

</div>

---

Estimate the **downstream impact** of a specific PyPI package version — how many
other projects would be affected if it had a vulnerability. It combines
[deps.dev](https://deps.dev) direct/indirect dependent counts with an optional
monthly-download figure into a single, conservative impact proxy you can use to
rank findings.

> The proxy is *ranking evidence*, not a precise affected-install count. PyPI
> does not expose reliable reverse-dependent download totals, so any such number
> is an estimate.

## Highlights

- Direct and indirect dependent counts from deps.dev
- Conservative, capped transitive-download proxy for ranking findings
- Never raises on missing data — returns an empty dict instead
- In-process caching, library and CLI interfaces

## Install

```bash
pip install pypi-blast-radius
```

## Library usage

```python
from pypi_blast_radius import estimate_blast_radius

result = estimate_blast_radius("requests", "2.31.0", direct_downloads=1_000_000)
print(result["direct_dependent_count"])         # from deps.dev
print(result["indirect_dependent_count"])       # from deps.dev
print(result["estimated_transitive_downloads"]) # bounded proxy
print(result["total_impact_score"])             # downloads + proxy
```

If deps.dev has no data for the version, or inputs are missing, an empty dict is
returned (never an exception).

## CLI

```bash
pypi-blast-radius requests 2.31.0 --downloads 1000000
pypi-blast-radius requests 2.31.0 --json
```

## How the proxy works

- `direct_dependent_count` and `indirect_dependent_count` come straight from
  deps.dev.
- `estimated_transitive_downloads = direct_downloads * min(10, log1p(direct + 0.2*indirect) * 0.9)`
  — indirect dependents are weighted lower, and the multiplier is capped at 10x
  so a huge dependent graph can't produce an absurd number.
- Results are cached in-process; call `clear_cache()` to reset.

## Development

```bash
git clone https://github.com/rahulreddykarne/pypi-blast-radius.git
cd pypi-blast-radius
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m build
```

Bug reports and pull requests are welcome on the [issue tracker](https://github.com/rahulreddykarne/pypi-blast-radius/issues).

## Related projects

Part of a small toolkit for Python supply-chain security research:

| Project | What it does |
| --- | --- |
| [pypi-bulk-download](https://github.com/rahulreddykarne/pypi-bulk-download) | Bulk-download top PyPI packages in parallel with safe unpacking. |
| [tarslip-guard](https://github.com/rahulreddykarne/tarslip-guard) | Detect unsafe extractall() calls and safely extract tar/zip archives. |
| [pypi-version-bisect](https://github.com/rahulreddykarne/pypi-version-bisect) | Find a vulnerability's affected version range in O(log n) checks. |
| [osv-dedupe](https://github.com/rahulreddykarne/osv-dedupe) | Score security findings against published OSV/NVD advisories. |
| [installtime-audit](https://github.com/rahulreddykarne/installtime-audit) | Flag install-time side effects in setup.py and friends. |
| [cvss-estimator](https://github.com/rahulreddykarne/cvss-estimator) | CVSS v3.1 calculator and evidence-driven vector estimator. |

## License

Released under the [MIT License](LICENSE).
